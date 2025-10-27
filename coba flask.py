from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import os
import tempfile
import zipfile
import shutil
import re
from werkzeug.utils import secure_filename
import easyocr
from pdf2image import convert_from_path
from PIL import Image

app = Flask(__name__)
app.secret_key = 'kunci-rahasia-untuk-flash-messages-2025'
POPPLER_PATH = r"C:\Program Files (x86)\poppler-24.08.0\Library\bin"
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg'}
ALLOWED_ZIP_EXTENSIONS = {'zip'}
ALLOWED_PDF_EXTENSIONS = {'pdf'}
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 * 1024  # 5 GB
reader = None

def init_ocr_reader():
    global reader
    if reader is None:
        reader = easyocr.Reader(['id', 'en'], gpu=False)
    return reader

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def extract_number_from_text(text):
    pattern = r'\d{10,16}'
    matches = re.findall(pattern, text)
    return matches[0] if matches else None

def process_image_with_ocr(image_path):
    ocr_reader = init_ocr_reader()
    results = ocr_reader.readtext(image_path)
    full_text = ' '.join([result[1] for result in results])
    return full_text

def rename_peta_process(input_folder, output_folder):
    results = {
        'success': 0,
        'anomali': 0,
        'files': []
    }
    
    anomali_counter = 1
    
    image_files = [f for f in os.listdir(input_folder) 
                   if allowed_file(f, ALLOWED_IMAGE_EXTENSIONS)]
    
    for idx, filename in enumerate(image_files, 1):
        input_path = os.path.join(input_folder, filename)
        extension = filename.rsplit('.', 1)[1].lower()
        
        try:
            text = process_image_with_ocr(input_path)
            
            number = extract_number_from_text(text)
            
            if number:
                new_filename = f"{number}.{extension}"
                results['success'] += 1
            else:
                new_filename = f"Anomali_{anomali_counter}.{extension}"
                anomali_counter += 1
                results['anomali'] += 1
            
            output_path = os.path.join(output_folder, new_filename)
            shutil.copy2(input_path, output_path)
            
            results['files'].append({
                'original': filename,
                'new': new_filename,
                'status': 'success' if number else 'anomali'
            })
            
        except Exception as e:
            new_filename = f"Anomali_{anomali_counter}.{extension}"
            anomali_counter += 1
            output_path = os.path.join(output_folder, new_filename)
            shutil.copy2(input_path, output_path)
            
            results['anomali'] += 1
            results['files'].append({
                'original': filename,
                'new': new_filename,
                'status': 'error',
                'error': str(e)
            })
    
    return results

def convert_pdf_to_jpg_process(pdf_path, output_folder):
    """
    Convert PDF ke JPG dengan path Poppler manual
    """
    results = {
        'total_pages': 0,
        'files': []
    }
    
    try:
        images = convert_from_path(
            pdf_path, 
            dpi=300,
            poppler_path=POPPLER_PATH
        )
        
        results['total_pages'] = len(images)
        
        for idx, image in enumerate(images, 1):
            output_filename = f"halaman_{idx}.jpg"
            output_path = os.path.join(output_folder, output_filename)
            
            image.save(output_path, 'JPEG', quality=95)
            
            results['files'].append({
                'page': idx,
                'filename': output_filename,
                'status': 'success'
            })
        
    except Exception as e:
        results['error'] = str(e)
    
    return results

def create_zip(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/rename')
def rename():
    return render_template('rename.html')

@app.route('/convert')
def convert():
    return render_template('convert.html')

@app.route('/process-rename', methods=['POST'])
def process_rename():
    if 'file' not in request.files:
        flash('Tidak ada file yang diupload', 'error')
        return redirect(url_for('rename'))
    
    files = request.files.getlist('file')
    
    if not files or files[0].filename == '':
        flash('Tidak ada file yang dipilih', 'error')
        return redirect(url_for('rename'))
    
    temp_dir = tempfile.mkdtemp()
    input_folder = os.path.join(temp_dir, 'input')
    output_folder = os.path.join(temp_dir, 'output')
    os.makedirs(input_folder)
    os.makedirs(output_folder)
    
    try:
        first_file = files[0]
        
        if allowed_file(first_file.filename, ALLOWED_ZIP_EXTENSIONS):
            zip_path = os.path.join(temp_dir, secure_filename(first_file.filename))
            first_file.save(zip_path)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(input_folder)
        else:
            for file in files:
                if file and allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(input_folder, filename))
        
        results = rename_peta_process(input_folder, output_folder)
        
        output_zip_path = os.path.join(temp_dir, 'hasil_rename.zip')
        create_zip(output_folder, output_zip_path)
        
        final_zip_path = os.path.join(tempfile.gettempdir(), f'hasil_rename_{os.getpid()}.zip')
        shutil.copy2(output_zip_path, final_zip_path)
        
        return render_template('result.html', 
                             result_type='rename',
                             results=results,
                             download_file=final_zip_path)
    
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'error')
        return redirect(url_for('rename'))
    finally:
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

@app.route('/process-convert', methods=['POST'])
def process_convert():
    if 'file' not in request.files:
        flash('Tidak ada file yang diupload', 'error')
        return redirect(url_for('convert'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('Tidak ada file yang dipilih', 'error')
        return redirect(url_for('convert'))
    
    if not allowed_file(file.filename, ALLOWED_PDF_EXTENSIONS):
        flash('File harus berformat PDF', 'error')
        return redirect(url_for('convert'))
    
    temp_dir = tempfile.mkdtemp()
    output_folder = os.path.join(temp_dir, 'output')
    os.makedirs(output_folder)
    
    try:
        pdf_path = os.path.join(temp_dir, secure_filename(file.filename))
        file.save(pdf_path)
        
        results = convert_pdf_to_jpg_process(pdf_path, output_folder)
        
        if 'error' in results:
            flash(f'Terjadi kesalahan: {results["error"]}', 'error')
            return redirect(url_for('convert'))
        
        output_zip_path = os.path.join(temp_dir, 'hasil_convert.zip')
        create_zip(output_folder, output_zip_path)
        
        final_zip_path = os.path.join(tempfile.gettempdir(), f'hasil_convert_{os.getpid()}.zip')
        shutil.copy2(output_zip_path, final_zip_path)
        
        return render_template('result.html',
                             result_type='convert',
                             results=results,
                             download_file=final_zip_path)
    
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'error')
        return redirect(url_for('convert'))
    finally:
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

@app.route('/download/<path:filename>')
def download(filename):
    try:
        return send_file(filename, 
                        as_attachment=True,
                        download_name=os.path.basename(filename))
    except Exception as e:
        flash(f'File tidak ditemukan: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.errorhandler(413)
def request_entity_too_large(error):
    flash('Ukuran file terlalu besar! Maksimum 5 GB.', 'error')
    return redirect(request.referrer or url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
