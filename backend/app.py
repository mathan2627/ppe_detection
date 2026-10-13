"""
Dual Mode Detection API: PPE Detection + Normal Object Detection
"""
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from ultralytics import YOLO
import cv2
import numpy as np
from pymongo import MongoClient
from datetime import datetime
import base64
import os
import csv
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch

app = Flask(__name__)
CORS(app)

# MongoDB setup
try:
    client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
    db = client['ppe_detection']
    detections_collection = db['detections']
    print("✓ MongoDB connected")
except Exception as e:
    print(f"⚠ MongoDB not available: {e}")
    detections_collection = None

# Load models
print("Loading detection models...")

# PPE Model - check multiple locations
ppe_model_paths = [
    'runs/detect/ppe_detection/weights/best.pt',
    'runs/detect/ppe_detection2/weights/best.pt',
    'runs/detect/ppe_detection3/weights/best.pt'
]

ppe_model_loaded = False
for ppe_model_path in ppe_model_paths:
    if os.path.exists(ppe_model_path):
        ppe_model = YOLO(ppe_model_path)
        print(f"✓ PPE model loaded: {ppe_model_path}")
        ppe_model_loaded = True
        break

if not ppe_model_loaded:
    print(f"⚠ PPE model not found, using fallback")
    ppe_model = YOLO('yolov8n.pt')

# Normal Detection Model
normal_model = YOLO('yolov8n.pt')
print(f"✓ Normal detection model loaded")

# Dataset classes - EXACT match from data.yaml
DATASET_CLASSES = [
    'Fall-Detected', 'Gloves', 'Goggles', 'Hardhat', 'Ladder', 'Mask', 
    'NO-Gloves', 'NO-Goggles', 'NO-Hardhat', 'NO-Mask', 'NO-Safety Vest', 
    'Person', 'Safety Cone', 'Safety Vest'
]

# Map dataset classes to standard PPE names
DATASET_CLASS_MAP = {
    'Hardhat': 'Helmet',
    'Safety Vest': 'Vest',
    'Gloves': 'Gloves',
    'Mask': 'Mask',
    'Goggles': 'Goggles',
    'Person': 'Person',
    'NO-Hardhat': 'NO-Helmet',
    'NO-Safety Vest': 'NO-Vest',
    'NO-Gloves': 'NO-Gloves',
    'NO-Mask': 'NO-Mask',
    'NO-Goggles': 'NO-Goggles',
    'Fall-Detected': 'Fall-Detected',
    'Ladder': 'Ladder',
    'Safety Cone': 'Safety Cone'
}

# Required PPE items - FLEXIBLE: Only Helmet is STRICTLY required
# Footwear (Boots OR Shoes) and Vest are checked but more lenient
REQUIRED_PPE_STRICT = ['Helmet']  # Must have
REQUIRED_PPE_RECOMMENDED = ['Vest', 'Gloves']  # Should have

# All PPE items to check (from dataset)
ALL_PPE_ITEMS = ['Mask', 'Vest', 'Goggles', 'Helmet', 'Gloves']

@app.route('/')
def home():
    return jsonify({
        'status': 'running',
        'message': 'Dual Mode Detection API',
        'modes': ['ppe', 'normal'],
        'ppe_classes': ALL_PPE_ITEMS,
        'required_ppe_strict': REQUIRED_PPE_STRICT,
        'required_ppe_recommended': REQUIRED_PPE_RECOMMENDED
    })

@app.route('/detect/image', methods=['POST'])
def detect_image():
    """Detect objects in uploaded image - saves EACH image separately"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        # Get detection mode and filename
        mode = request.form.get('mode', 'ppe')  # 'ppe' or 'normal'
        filename = request.form.get('filename', 'unknown.jpg')
        
        file = request.files['image']
        image_bytes = file.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({'error': 'Invalid image'}), 400
        
        # Select model based on mode
        if mode == 'ppe':
            results = ppe_model(image, conf=0.15, verbose=False)  # LOWER confidence for better detection
            result_data = process_ppe_detection(results, image)
        else:
            results = normal_model(image, conf=0.25, verbose=False)
            result_data = process_normal_detection(results, image)
        
        # Save EACH image detection to database with COMPLETE information
        if detections_collection is not None:
            try:
                detection_record = {
                    'timestamp': datetime.now(),
                    'mode': mode,
                    'type': 'image',
                    'filename': filename,
                    'detections': result_data['detections'],
                    'compliance': result_data.get('compliance'),
                    'statistics': result_data.get('statistics'),
                    'image_base64': result_data.get('image'),
                    'total_objects': len(result_data['detections']),
                    'detection_summary': generate_detection_summary(result_data, mode),
                    'object_categories': result_data.get('object_categories', {}),
                    'detections_by_category': result_data.get('detections_by_category', {}),
                    'unique_classes': len(result_data.get('object_categories', {}))
                }
                inserted = detections_collection.insert_one(detection_record)
                result_data['record_id'] = str(inserted.inserted_id)
                print(f"✓ Saved detection to DB: {inserted.inserted_id} - {filename}")
                print(f"  Mode: {mode.upper()}, Objects: {len(result_data['detections'])}, Categories: {len(result_data.get('object_categories', {}))}")
            except Exception as e:
                print(f"Database save error: {e}")
        
        return jsonify(result_data)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def process_ppe_detection(results, image):
    """Process PPE detection results - ONLY PPE items, filter out everything else INCLUDING PERSON"""
    detections = []
    detected_ppe = {}  # Count each PPE item
    filtered_count = 0  # Count of non-PPE items filtered out
    
    # ONLY THESE PPE ITEMS - NO PERSON!
    ALLOWED_PPE_ONLY = ['Helmet', 'Vest', 'Mask', 'Gloves', 'Goggles']
    
    for result in results:
        boxes = result.boxes
        
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            
            # Get class name from model
            class_name = result.names[cls] if hasattr(result, 'names') else f'class_{cls}'
            
            # Map to standard name
            class_name = DATASET_CLASS_MAP.get(class_name, class_name)
            
            # STRICT FILTER: ONLY PPE items, NO PERSON, NO OTHER OBJECTS
            if class_name in ALLOWED_PPE_ONLY:
                detected_ppe[class_name] = detected_ppe.get(class_name, 0) + 1
                detections.append({
                    'bbox': [float(x1), float(y1), float(x2), float(y2)],
                    'confidence': round(conf, 2),
                    'class': class_name
                })
                print(f"  ✓ Detected PPE: {class_name} ({conf:.2f})")
            else:
                # Filter out everything else including Person
                filtered_count += 1
                print(f"  ✗ Filtered non-PPE: {class_name}")
    
    # Draw results on image with SMALLER text
    annotated = image.copy()
    
    for det in detections:
        x1, y1, x2, y2 = [int(v) for v in det['bbox']]
        
        # Color based on PPE type
        if det['class'] in ['Helmet']:
            color = (0, 255, 0)  # Green for helmet
        elif det['class'] == 'Vest':
            color = (0, 165, 255)  # Orange for vest
        elif det['class'] in ['Mask', 'Goggles']:
            color = (255, 255, 0)  # Cyan for face protection
        elif det['class'] == 'Gloves':
            color = (255, 0, 255)  # Magenta for gloves
        else:
            color = (0, 200, 255)  # Default cyan
        
        # Draw rectangle
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        
        # SMALLER text - reduced font size
        label = f"{det['class']} {det['confidence']:.2f}"
        font_scale = 0.4  # SMALLER font
        thickness = 1  # Thinner text
        (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
        
        # Background for text
        cv2.rectangle(annotated, (x1, y1 - h - 4), (x1 + w + 4, y1), color, -1)
        
        # SMALLER text
        cv2.putText(annotated, label, (x1 + 2, y1 - 2), 
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)
    
    # Convert to base64
    _, buffer = cv2.imencode('.jpg', annotated)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    
    # Check compliance - FLEXIBLE RULES
    detected_ppe_list = list(detected_ppe.keys())
    
    # Check what's detected
    has_helmet = 'Helmet' in detected_ppe_list
    has_vest = 'Vest' in detected_ppe_list
    has_gloves = 'Gloves' in detected_ppe_list
    
    # Build missing items list
    missing_items = []
    if not has_helmet:
        missing_items.append('Helmet')
    if not has_vest:
        missing_items.append('Vest')
    if not has_gloves:
        missing_items.append('Gloves')
    
    # For PPE mode, we assume person is present if PPE is detected
    person_count = 1 if len(detected_ppe) > 0 else 0
    
    # FLEXIBLE SAFETY: SAFE if ANY PPE detected (not just required ones)
    # This helps when model doesn't detect everything perfectly
    if person_count == 0:
        is_safe = False
        compliance_score = 0
        status_message = "No PPE detected"
    elif len(detected_ppe) == 0:
        is_safe = False
        compliance_score = 0
        status_message = "No PPE detected"
    elif has_helmet and (has_vest or has_gloves):
        # SAFE if helmet + at least one other PPE item
        is_safe = True
        compliance_score = 100 if len(missing_items) == 0 else 75
        if len(missing_items) == 0:
            status_message = "All required PPE detected - SAFE"
        else:
            status_message = f"SAFE - Core PPE detected (Missing: {', '.join(missing_items)})"
    elif len(detected_ppe) >= 2:
        # SAFE if at least 2 PPE items detected
        is_safe = True
        compliance_score = 60
        status_message = f"SAFE - Multiple PPE items detected (Missing: {', '.join(missing_items)})"
    else:
        # NOT SAFE - only 1 or no PPE items
        is_safe = False
        compliance_score = 30
        status_message = f"NOT SAFE - Insufficient PPE (Missing: {', '.join(missing_items)})"
    
    compliance = {
        'is_safe': is_safe,
        'status_message': status_message,
        'detected_ppe': detected_ppe,
        'detected_ppe_list': detected_ppe_list,
        'missing_required': missing_items,
        'not_found_ppe': [item for item in ALL_PPE_ITEMS if item not in detected_ppe_list],
        'compliance_score': round(compliance_score, 2),
        'person_count': person_count,
        'total_ppe_items': sum(detected_ppe.values()),
        'filtered_non_ppe_count': filtered_count
    }
    
    # Create detailed object list for each PPE category
    object_categories = {
        'Helmet': detected_ppe.get('Helmet', 0),
        'Vest': detected_ppe.get('Vest', 0),
        'Mask': detected_ppe.get('Mask', 0),
        'Gloves': detected_ppe.get('Gloves', 0),
        'Goggles': detected_ppe.get('Goggles', 0)
    }
    
    # Detailed detection list by category
    detections_by_category = {}
    for det in detections:
        cat = det['class']
        if cat not in detections_by_category:
            detections_by_category[cat] = []
        detections_by_category[cat].append({
            'confidence': det['confidence'],
            'bbox': det['bbox']
        })
    
    print(f"  ✓ PPE Detection Summary: {len(detections)} PPE items, {filtered_count} non-PPE filtered")
    
    return {
        'mode': 'ppe',
        'detections': detections,
        'compliance': compliance,
        'image': img_base64,
        'statistics': {
            'total_detections': len(detections),
            'person_count': person_count,
            'ppe_items_detected': detected_ppe,
            'required_ppe_status': {item: item in detected_ppe_list for item in REQUIRED_PPE_STRICT + REQUIRED_PPE_RECOMMENDED},
            'filtered_non_ppe': filtered_count
        },
        'object_categories': object_categories,
        'detections_by_category': detections_by_category
    }

def process_normal_detection(results, image):
    """Process normal object detection results"""
    detections = []
    class_counts = {}
    
    for result in results:
        boxes = result.boxes
        
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            
            class_name = result.names[cls] if hasattr(result, 'names') else f'class_{cls}'
            
            detections.append({
                'bbox': [float(x1), float(y1), float(x2), float(y2)],
                'confidence': round(conf, 2),
                'class': class_name
            })
            
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
    
    # Draw results on image with better visibility
    annotated = image.copy()
    
    for det in detections:
        x1, y1, x2, y2 = [int(v) for v in det['bbox']]
        
        # Bright colors for better visibility
        color_map = {
            'person': (255, 100, 0),  # Orange
            'car': (0, 255, 255),     # Cyan
            'truck': (255, 0, 255),   # Magenta
            'bus': (255, 255, 0),     # Yellow
            'bicycle': (0, 255, 0),   # Green
            'motorcycle': (255, 0, 0) # Red
        }
        
        class_lower = det['class'].lower()
        if class_lower in color_map:
            color = color_map[class_lower]
        else:
            # Generate bright color based on class name
            h = hash(det['class'])
            color = (
                (h % 200) + 55,
                ((h * 2) % 200) + 55,
                ((h * 3) % 200) + 55
            )
        
        # Thicker rectangle
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 3)
        
        # Larger yellow dot at center
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        cv2.circle(annotated, (cx, cy), 8, (0, 255, 255), -1)
        cv2.circle(annotated, (cx, cy), 10, (0, 0, 0), 2)  # Black outline
        
        # Label with better background
        label = f"{det['class']} {det['confidence']:.2f}"
        (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(annotated, (x1, y1 - 25), (x1 + w + 10, y1), color, -1)
        cv2.putText(annotated, label, (x1 + 5, y1 - 7), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Convert to base64
    _, buffer = cv2.imencode('.jpg', annotated)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    
    # Detailed detection list by category
    detections_by_category = {}
    for det in detections:
        cat = det['class']
        if cat not in detections_by_category:
            detections_by_category[cat] = []
        detections_by_category[cat].append({
            'confidence': det['confidence'],
            'bbox': det['bbox']
        })
    
    # Sort class counts by count (descending)
    sorted_class_counts = dict(sorted(class_counts.items(), key=lambda x: x[1], reverse=True))
    
    return {
        'mode': 'normal',
        'detections': detections,
        'image': img_base64,
        'statistics': {
            'total_detections': len(detections),
            'class_counts': sorted_class_counts,
            'unique_classes': len(class_counts)
        },
        'object_categories': sorted_class_counts,
        'detections_by_category': detections_by_category
    }

def generate_detection_summary(result_data, mode):
    """Generate human-readable summary for database"""
    if mode == 'ppe':
        comp = result_data.get('compliance', {})
        detected_ppe = comp.get('detected_ppe', {})
        summary = f"Status: {'SAFE' if comp.get('is_safe') else 'NOT SAFE'}, "
        summary += f"Score: {comp.get('compliance_score', 0)}%, "
        summary += f"Persons: {comp.get('person_count', 0)}, "
        summary += f"PPE Items: {', '.join([f'{k}:{v}' for k, v in detected_ppe.items()])}"
        return summary
    else:
        stats = result_data.get('statistics', {})
        class_counts = stats.get('class_counts', {})
        summary = f"Objects: {stats.get('total_detections', 0)}, "
        summary += f"Classes: {stats.get('unique_classes', 0)}, "
        summary += f"Top: {', '.join([f'{k}:{v}' for k, v in list(class_counts.items())[:5]])}"
        return summary

@app.route('/detect/video', methods=['POST'])
def detect_video():
    """Detect objects in uploaded video - saves to DB"""
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video provided'}), 400
        
        # Get detection mode and filename
        mode = request.form.get('mode', 'ppe')
        filename = request.form.get('filename', 'unknown.mp4')
        
        file = request.files['video']
        
        # Save video temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
            file.save(tmp.name)
            video_path = tmp.name
        
        # Process video - extract middle frame for detection
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        middle_frame = total_frames // 2
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame)
        ret, frame = cap.read()
        cap.release()
        
        # Clean up temp file
        os.remove(video_path)
        
        if not ret or frame is None:
            return jsonify({'error': 'Could not read video'}), 400
        
        # Select model based on mode
        if mode == 'ppe':
            results = ppe_model(frame, conf=0.25, verbose=False)
            result_data = process_ppe_detection(results, frame)
        else:
            results = normal_model(frame, conf=0.25, verbose=False)
            result_data = process_normal_detection(results, frame)
        
        # Save video detection to database with COMPLETE information
        if detections_collection is not None:
            try:
                detection_record = {
                    'timestamp': datetime.now(),
                    'mode': mode,
                    'type': 'video',
                    'filename': filename,
                    'detections': result_data['detections'],
                    'compliance': result_data.get('compliance'),
                    'statistics': result_data.get('statistics'),
                    'image_base64': result_data.get('image'),
                    'total_objects': len(result_data['detections']),
                    'detection_summary': generate_detection_summary(result_data, mode),
                    'object_categories': result_data.get('object_categories', {}),
                    'detections_by_category': result_data.get('detections_by_category', {}),
                    'unique_classes': len(result_data.get('object_categories', {}))
                }
                inserted = detections_collection.insert_one(detection_record)
                result_data['record_id'] = str(inserted.inserted_id)
                print(f"✓ Saved video detection to DB: {inserted.inserted_id} - {filename}")
                print(f"  Mode: {mode.upper()}, Objects: {len(result_data['detections'])}, Categories: {len(result_data.get('object_categories', {}))}")
            except Exception as e:
                print(f"Database save error: {e}")
        
        return jsonify(result_data)
        
    except Exception as e:
        print(f"Video detection error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/analytics', methods=['GET'])
def get_analytics():
    """Get detailed analytics from DATABASE"""
    try:
        mode = request.args.get('mode', 'ppe')
        
        if detections_collection is None:
            return jsonify({
                'mode': mode,
                'total_detections': 0,
                'records': []
            })
        
        # Get ALL detections from database for the mode
        query = {'mode': mode} if mode else {}
        all_detections = list(detections_collection.find(query).sort('timestamp', -1).limit(500))
        
        # Convert to detailed records with COMPLETE information
        records = []
        for d in all_detections:
            record = {
                'id': str(d.get('_id', '')),
                'timestamp': d['timestamp'].isoformat() if isinstance(d['timestamp'], datetime) else str(d['timestamp']),
                'mode': d.get('mode', 'unknown'),
                'type': d.get('type', 'unknown'),
                'filename': d.get('filename', 'N/A'),
                'total_objects': d.get('total_objects', len(d.get('detections', []))),
                'detections': d.get('detections', []),
                'detection_summary': d.get('detection_summary', ''),
                'object_categories': d.get('object_categories', {}),
                'detections_by_category': d.get('detections_by_category', {}),
                'unique_classes': d.get('unique_classes', 0)
            }
            
            # Add mode-specific data
            if mode == 'ppe':
                comp = d.get('compliance', {})
                record['status'] = 'SAFE' if comp.get('is_safe') else 'NOT SAFE'
                record['compliance_score'] = comp.get('compliance_score', 0)
                record['person_count'] = comp.get('person_count', 0)
                record['detected_ppe'] = comp.get('detected_ppe', {})
                record['missing_required'] = comp.get('missing_required', [])
                
                # Individual PPE counts
                obj_cats = d.get('object_categories', {})
                record['helmet'] = obj_cats.get('Helmet', 0)
                record['vest'] = obj_cats.get('Vest', 0)
                record['boots'] = obj_cats.get('Boots', 0)
                record['mask'] = obj_cats.get('Mask', 0)
                record['gloves'] = obj_cats.get('Gloves', 0)
                record['glasses'] = obj_cats.get('Glasses', 0)
                record['goggles'] = obj_cats.get('Goggles', 0)
                record['shoes'] = obj_cats.get('Shoes', 0)
                
                # Detailed list of each object
                record['object_list'] = []
                for cat, items in d.get('detections_by_category', {}).items():
                    for idx, item in enumerate(items, 1):
                        record['object_list'].append({
                            'category': cat,
                            'number': idx,
                            'confidence': item['confidence'],
                            'label': f"{cat} #{idx}"
                        })
            else:
                stats = d.get('statistics', {})
                record['unique_classes'] = d.get('unique_classes', stats.get('unique_classes', 0))
                record['class_counts'] = d.get('object_categories', stats.get('class_counts', {}))
                
                # Detailed list of each object
                record['object_list'] = []
                for cat, items in d.get('detections_by_category', {}).items():
                    for idx, item in enumerate(items, 1):
                        record['object_list'].append({
                            'category': cat,
                            'number': idx,
                            'confidence': item['confidence'],
                            'label': f"{cat} #{idx}"
                        })
            
            records.append(record)
        
        # Summary statistics
        total = len(records)
        summary = {
            'total_detections': total,
            'image_count': sum(1 for r in records if r['type'] == 'image'),
            'video_count': sum(1 for r in records if r['type'] == 'video'),
            'live_count': sum(1 for r in records if r['type'] == 'live')
        }
        
        if mode == 'ppe':
            summary['safe_count'] = sum(1 for r in records if r.get('status') == 'SAFE')
            summary['violation_count'] = total - summary['safe_count']
            summary['compliance_rate'] = round((summary['safe_count'] / total * 100) if total > 0 else 0, 2)
        
        return jsonify({
            'mode': mode,
            'summary': summary,
            'records': records
        })
            
    except Exception as e:
        print(f"Analytics error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def get_ppe_analytics(detections):
    """Get PPE analytics with detailed records"""
    total = len(detections)
    safe_count = sum(1 for d in detections if d.get('compliance', {}).get('is_safe', False))
    
    compliance_rate = (safe_count / total * 100) if total > 0 else 0
    
    # Count missing items
    missing_items_freq = {}
    ppe_items_freq = {}
    person_total = 0
    
    for d in detections:
        # Missing items
        for item in d.get('compliance', {}).get('missing_required', []):
            missing_items_freq[item] = missing_items_freq.get(item, 0) + 1
        
        # Detected PPE items
        detected_ppe = d.get('compliance', {}).get('detected_ppe', {})
        for item, count in detected_ppe.items():
            ppe_items_freq[item] = ppe_items_freq.get(item, 0) + count
        
        # Person count
        person_total += d.get('compliance', {}).get('person_count', 0)
    
    # Detailed records for table
    detailed_records = []
    for d in detections:
        comp = d.get('compliance', {})
        detected_ppe = comp.get('detected_ppe', {})
        
        record = {
            'id': str(d.get('_id', '')),
            'timestamp': d['timestamp'].isoformat() if isinstance(d['timestamp'], datetime) else str(d['timestamp']),
            'status': 'SAFE' if comp.get('is_safe') else 'NOT SAFE',
            'compliance_score': comp.get('compliance_score', 0),
            'person_count': comp.get('person_count', 0),
            'total_detections': len(d.get('detections', [])),
            'detected_ppe': detected_ppe,
            'detected_ppe_list': list(detected_ppe.keys()),
            'missing_required': comp.get('missing_required', []),
            'helmet_count': detected_ppe.get('Helmet', 0),
            'vest_count': detected_ppe.get('Vest', 0),
            'boots_count': detected_ppe.get('Boots', 0),
            'mask_count': detected_ppe.get('Mask', 0),
            'gloves_count': detected_ppe.get('Gloves', 0),
            'glasses_count': detected_ppe.get('Glasses', 0),
            'goggles_count': detected_ppe.get('Goggles', 0),
            'shoes_count': detected_ppe.get('Shoes', 0)
        }
        detailed_records.append(record)
    
    return {
        'mode': 'ppe',
        'total_detections': total,
        'safe_count': safe_count,
        'violation_count': total - safe_count,
        'compliance_rate': round(compliance_rate, 2),
        'missing_items_frequency': missing_items_freq,
        'ppe_items_detected': ppe_items_freq,
        'total_persons_detected': person_total,
        'detailed_records': detailed_records,
        'summary': {
            'most_missing_ppe': max(missing_items_freq.items(), key=lambda x: x[1])[0] if missing_items_freq else 'None',
            'most_detected_ppe': max(ppe_items_freq.items(), key=lambda x: x[1])[0] if ppe_items_freq else 'None',
            'average_persons_per_detection': round(person_total / total, 2) if total > 0 else 0
        }
    }

def get_normal_analytics(detections):
    """Get normal detection analytics with detailed records"""
    total = len(detections)
    
    class_freq = {}
    total_objects = 0
    
    for d in detections:
        stats = d.get('statistics', {})
        class_counts = stats.get('class_counts', {})
        
        for cls, count in class_counts.items():
            class_freq[cls] = class_freq.get(cls, 0) + count
            total_objects += count
    
    # Detailed records for table
    detailed_records = []
    for d in detections:
        stats = d.get('statistics', {})
        class_counts = stats.get('class_counts', {})
        
        record = {
            'id': str(d.get('_id', '')),
            'timestamp': d['timestamp'].isoformat() if isinstance(d['timestamp'], datetime) else str(d['timestamp']),
            'total_objects': stats.get('total_detections', 0),
            'unique_classes': stats.get('unique_classes', 0),
            'class_counts': class_counts,
            'top_3_classes': ', '.join([f"{k}:{v}" for k, v in sorted(class_counts.items(), key=lambda x: x[1], reverse=True)[:3]])
        }
        detailed_records.append(record)
    
    return {
        'mode': 'normal',
        'total_detections': total,
        'total_objects_detected': total_objects,
        'class_frequency': class_freq,
        'unique_classes': len(class_freq),
        'average_objects_per_detection': round(total_objects / total, 2) if total > 0 else 0,
        'top_classes': sorted(class_freq.items(), key=lambda x: x[1], reverse=True)[:10],
        'detailed_records': detailed_records
    }

@app.route('/export/csv/<record_id>', methods=['GET'])
def export_single_csv(record_id):
    """Export single detection record to CSV"""
    try:
        from bson.objectid import ObjectId
        
        if detections_collection is None:
            return jsonify({'error': 'Database not available'}), 500
        
        detection = detections_collection.find_one({'_id': ObjectId(record_id)})
        if not detection:
            return jsonify({'error': 'Record not found'}), 404
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header info
        writer.writerow(['Detection Report'])
        writer.writerow(['Timestamp', detection['timestamp'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(detection['timestamp'], datetime) else str(detection['timestamp'])])
        writer.writerow(['Mode', detection.get('mode', 'N/A').upper()])
        writer.writerow(['Type', detection.get('type', 'N/A').upper()])
        writer.writerow(['Filename', detection.get('filename', 'N/A')])
        writer.writerow([])
        
        # Mode-specific summary
        if detection.get('mode') == 'ppe':
            comp = detection.get('compliance', {})
            writer.writerow(['Status', 'SAFE' if comp.get('is_safe') else 'NOT SAFE'])
            writer.writerow(['Compliance Score', f"{comp.get('compliance_score', 0)}%"])
            writer.writerow(['Person Count', comp.get('person_count', 0)])
            writer.writerow([])
            
            writer.writerow(['PPE Items Detected'])
            detected_ppe = comp.get('detected_ppe', {})
            for item, count in detected_ppe.items():
                writer.writerow([item, count])
            writer.writerow([])
            
            if comp.get('missing_required'):
                writer.writerow(['Missing Required PPE'])
                for item in comp.get('missing_required', []):
                    writer.writerow([item])
                writer.writerow([])
        else:
            stats = detection.get('statistics', {})
            writer.writerow(['Total Objects', stats.get('total_detections', 0)])
            writer.writerow(['Unique Classes', stats.get('unique_classes', 0)])
            writer.writerow([])
            
            writer.writerow(['Class Counts'])
            for cls, count in stats.get('class_counts', {}).items():
                writer.writerow([cls, count])
            writer.writerow([])
        
        # All detections
        writer.writerow(['All Detections'])
        writer.writerow(['Class', 'Confidence', 'BBox X1', 'BBox Y1', 'BBox X2', 'BBox Y2'])
        for det in detection.get('detections', []):
            bbox = det.get('bbox', [0, 0, 0, 0])
            writer.writerow([
                det.get('class', 'Unknown'),
                det.get('confidence', 0),
                round(bbox[0], 2),
                round(bbox[1], 2),
                round(bbox[2], 2),
                round(bbox[3], 2)
            ])
        
        output.seek(0)
        filename = f"detection_{record_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"CSV export error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/export/pdf/<record_id>', methods=['GET'])
def export_single_pdf(record_id):
    """Export single detection record to PDF"""
    try:
        from bson.objectid import ObjectId
        
        if detections_collection is None:
            return jsonify({'error': 'Database not available'}), 500
        
        detection = detections_collection.find_one({'_id': ObjectId(record_id)})
        if not detection:
            return jsonify({'error': 'Record not found'}), 404
        
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title = Paragraph(f"<b>Detection Report</b>", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        # Summary info
        timestamp = detection['timestamp'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(detection['timestamp'], datetime) else str(detection['timestamp'])
        mode = detection.get('mode', 'N/A').upper()
        det_type = detection.get('type', 'N/A').upper()
        filename = detection.get('filename', 'N/A')
        
        summary_text = f"<b>Timestamp:</b> {timestamp}<br/>"
        summary_text += f"<b>Mode:</b> {mode}<br/>"
        summary_text += f"<b>Type:</b> {det_type}<br/>"
        summary_text += f"<b>Filename:</b> {filename}<br/>"
        
        if detection.get('mode') == 'ppe':
            comp = detection.get('compliance', {})
            status = 'SAFE' if comp.get('is_safe') else 'NOT SAFE'
            summary_text += f"<b>Status:</b> {status}<br/>"
            summary_text += f"<b>Compliance Score:</b> {comp.get('compliance_score', 0)}%<br/>"
            summary_text += f"<b>Persons:</b> {comp.get('person_count', 0)}<br/>"
            
            detected_ppe = comp.get('detected_ppe', {})
            if detected_ppe:
                summary_text += f"<b>PPE Items:</b> {', '.join([f'{k}:{v}' for k, v in detected_ppe.items()])}<br/>"
            
            if comp.get('missing_required'):
                summary_text += f"<b>Missing:</b> {', '.join(comp.get('missing_required', []))}<br/>"
        else:
            stats = detection.get('statistics', {})
            summary_text += f"<b>Total Objects:</b> {stats.get('total_detections', 0)}<br/>"
            summary_text += f"<b>Unique Classes:</b> {stats.get('unique_classes', 0)}<br/>"
        
        elements.append(Paragraph(summary_text, styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Detections Table
        detections_list = detection.get('detections', [])
        if detections_list:
            elements.append(Paragraph("<b>All Detections:</b>", styles['Heading2']))
            elements.append(Spacer(1, 0.1*inch))
            
            data = [['Class', 'Confidence', 'BBox']]
            for det in detections_list[:30]:  # Limit to 30 for PDF
                bbox = det.get('bbox', [0, 0, 0, 0])
                bbox_str = f"({bbox[0]:.0f}, {bbox[1]:.0f}, {bbox[2]:.0f}, {bbox[3]:.0f})"
                data.append([
                    det.get('class', 'Unknown'),
                    f"{det.get('confidence', 0):.2f}",
                    bbox_str
                ])
            
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9)
            ]))
            
            elements.append(table)
        
        doc.build(elements)
        buffer.seek(0)
        
        filename = f"detection_{record_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"PDF export error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Dual Mode Detection API Starting...")
    print("="*60)
    print(f"PPE Model: {ppe_model_path if os.path.exists(ppe_model_path) else 'yolov8n.pt (FALLBACK)'}")
    print(f"Normal Model: yolov8n.pt")
    print(f"PPE Items: {', '.join(ALL_PPE_ITEMS)}")
    print(f"Required PPE (Strict): {', '.join(REQUIRED_PPE_STRICT)}")
    print(f"Required PPE (Recommended): {', '.join(REQUIRED_PPE_RECOMMENDED)}")
    print("="*60)
    print("Backend: http://localhost:5000")
    print("Modes: PPE Detection | Normal Detection")
    print("="*60 + "\n")
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True, use_reloader=False)
