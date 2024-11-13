from flask import Flask, render_template, request, redirect, url_for, session
import fitz  # PyMuPDF
from io import BytesIO
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key'  

@app.route('/')
def index():
    return render_template('index.html')  

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    file = request.files.get('pdf_file')
    if file:
        
        file_path = f"uploads/{file.filename}"
        file.save(file_path)
        session['pdf_path'] = file_path
        session['page_num'] = 0 
        return redirect(url_for('view_pdf'))
    return redirect(url_for('index'))



@app.route('/view_pdf')
def view_pdf():
    pdf_path = session.get('pdf_path', None)
    page_num = session.get('page_num', 0)

    if not pdf_path:
        return redirect(url_for('index'))
    
    
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_num) 
    pix = page.get_pixmap()  
    img_io = BytesIO(pix.tobytes("png"))  

    
    img_data = base64.b64encode(img_io.getvalue()).decode('utf-8')

    page_count = doc.page_count
    return render_template('view_pdf.html', img_data=img_data, page_num=page_num, page_count=page_count)


@app.route('/next')
def next_page():
    session['page_num'] = min(session.get('page_num', 0) + 1, session.get('page_count', 0) - 1)  # Set maximum limit
    return redirect(url_for('view_pdf'))

@app.route('/prev')
def prev_page():
    session['page_num'] = max(0, session.get('page_num', 0) - 1)
    return redirect(url_for('view_pdf'))

if __name__ == '__main__':
    app.run(debug=True)
