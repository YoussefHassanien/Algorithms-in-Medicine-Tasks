import gradio as gr
import random
import os
import base64

# Global variables
original_depth = None
min_chunk_size = 5
fixed_security_level = 3  # Fixed security level (no slider)

def encrypt_chunk(chunk, shift):
    return ''.join(chr((ord(c) + shift) % 256) for c in chunk)

def decrypt_chunk(chunk, shift):
    return ''.join(chr((ord(c) - shift) % 256) for c in chunk)

def get_shift(index):
    return 3 + index

def divide_and_conquer_encrypt(message, depth, index=0):
    global min_chunk_size
    if len(message) <= min_chunk_size:
        for i in range(depth - 1):
            shift = get_shift(index)
            encrypt_chunk(message, shift)
        return encrypt_chunk(message, shift)
    
    mid = max(len(message) // 2, min_chunk_size)
    left = divide_and_conquer_encrypt(message[:mid], depth, index)
    right = divide_and_conquer_encrypt(message[mid:], depth, index + 1)
    return left + right

def divide_and_conquer_decrypt(message, depth, original_depth, index=0):
    global min_chunk_size
    if depth != original_depth:
        return ''.join(random.choice('0123456789ABCDEF') for _ in range(len(message)))
    
    if len(message) <= min_chunk_size:
        for i in range(depth - 1):
            shift = get_shift(index)
            decrypt_chunk(message, shift)
        return decrypt_chunk(message, shift)
    
    mid = max(len(message) // 2, min_chunk_size)
    left = divide_and_conquer_decrypt(message[:mid], depth, depth, index)
    right = divide_and_conquer_decrypt(message[mid:], depth, depth, index + 1)
    return left + right

def encrypt_message(patient_name, age, gender, address, phone, emergency_contact, insurance, medical_history, diagnosis):
    global original_depth
    if not patient_name or not diagnosis:
        return "Please fill in all required fields"
    
    combined_message = (
        f"Name: {patient_name}; Age: {age}; Gender: {gender}; Address: {address}; "
        f"Phone: {phone}; Emergency Contact: {emergency_contact}; Insurance: {insurance}; "
        f"Medical History: {medical_history}; Diagnosis: {diagnosis}"
    )
    original_depth = fixed_security_level  # Use fixed security level
    
    # Encrypt and then base64 encode
    encrypted_message = divide_and_conquer_encrypt(combined_message, fixed_security_level)
    return base64.b64encode(encrypted_message.encode('utf-8')).decode('utf-8')

def save_encrypted_data(encrypted_message):
    if not encrypted_message or encrypted_message == "Please fill in all required fields":
        return "No data to save"
    
    # Create a directory for encrypted files if it doesn't exist
    os.makedirs('encrypted_data', exist_ok=True)
    
    # Generate a unique filename based on timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'encrypted_data/patient_data_{timestamp}.txt'
    
    # Save the base64 encoded encrypted message
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(encrypted_message)
        return f"Data saved successfully to {filename}"
    except Exception as e:
        return f"Error saving file: {str(e)}"

def read_uploaded_file(file):
    """
    Read the content of an uploaded file.
    
    Args:
    file (dict): Gradio file upload dictionary
    
    Returns:
    str: Content of the file
    """
    if file is None:
        return ""
    
    try:
        # Check if file is a dictionary from Gradio upload
        if isinstance(file, dict):
            file_path = file['name']
        elif hasattr(file, 'name'):
            # Handle temporary file wrapper
            file_path = file.name
        else:
            # Direct file path
            file_path = file
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def decrypt_message(encrypted_message):
    global original_depth
    if not encrypted_message:
        return []

    try:
        # Ensure original_depth is set for the decryption
        if original_depth is None:
            original_depth = fixed_security_level
        
        # Decode base64 first
        decoded_message = base64.b64decode(encrypted_message).decode('utf-8')
        
        # Then decrypt
        decrypted_data = divide_and_conquer_decrypt(decoded_message, fixed_security_level, original_depth)
        
        # Parse the decrypted data into a dictionary
        fields = [field.strip() for field in decrypted_data.split(";") if field]
        data = [[field.split(":")[0].strip(), field.split(":")[1].strip()] for field in fields]
        return data
    except Exception as e:
        return [["Error", str(e)]]

# Custom theme for colors
custom_theme = gr.themes.Base(
    primary_hue="blue",   # Set the primary color (button, slider, etc.)
    secondary_hue="green", # Set secondary color (background, etc.)
    neutral_hue="gray",    # Set neutral color
)

# Modern Layout with Gradio
with gr.Blocks(title="Hospital Registration Encryption Tool", theme=custom_theme) as app:
    gr.Markdown("## 🏥  Hospital Registration Encryption Tool")
    gr.Markdown("Securely store and transmit sensitive patient information.")

    with gr.Tabs():
        # Encryption Tab
        with gr.Tab("Encrypt Data"):
            gr.Markdown("### 📋 Patient Registration Form")
            with gr.Row():
                with gr.Column():
                    patient_name = gr.Textbox(label="Patient Name", placeholder="Enter full name", interactive=True, elem_id="patient-name")
                    age = gr.Number(label="Age", value=0, interactive=True, elem_id="age")
                    gender = gr.Radio(choices=["Male", "Female"], label="Gender", interactive=True, elem_classes=["gr-radio-row"])
                    address = gr.Textbox(label="Address", placeholder="Enter full address", interactive=True, elem_id="address")
                with gr.Column():
                    phone = gr.Textbox(label="Phone Number", placeholder="Enter phone number", interactive=True, elem_id="phone")
                    emergency_contact = gr.Textbox(label="Emergency Contact", placeholder="Enter emergency contact details", interactive=True, elem_id="emergency-contact")
                    insurance = gr.Textbox(label="Insurance Provider", placeholder="Enter insurance provider name", interactive=True, elem_id="insurance")
                    medical_history = gr.Textbox(label="Medical History", placeholder="Enter medical history details", interactive=True, elem_id="medical-history")
            gr.Markdown("---")
            with gr.Row():
                diagnosis = gr.Textbox(label="Diagnosis", placeholder="Enter diagnosis details", interactive=True, lines=2, elem_id="diagnosis")
            encrypt_output = gr.Textbox(label="Encrypted Registration Data", interactive=False, elem_id="encrypt-output")
            encrypt_button = gr.Button("Encrypt Data", elem_id="encrypt-btn")
            save_button = gr.Button("Save Encrypted Data", elem_id="save-btn")
            
            encrypt_button.click(
                fn=encrypt_message,
                inputs=[patient_name, age, gender, address, phone, emergency_contact, insurance, medical_history, diagnosis],
                outputs=encrypt_output
            )
            
            save_button.click(
                fn=save_encrypted_data,
                inputs=encrypt_output,
                outputs=encrypt_output
            )

        # Decryption Tab
        with gr.Tab("Decrypt Data"):
            gr.Markdown("### 🔓 Decrypt Encrypted Data")
            with gr.Row():
                # File upload component
                file_input = gr.File(label="Browse Encrypted File", type="filepath")
                decrypt_input = gr.Textbox(label="Encrypted Data", placeholder="Encrypted text will appear here", interactive=False, lines=3, elem_id="decrypt-input")
            
            decrypted_data_output = gr.Dataframe(
                headers=["Field", "Value"], 
                datatype=["str", "str"], 
                label="Decrypted Registration Data", interactive=False, elem_id="decrypted-data-output"
            )
            
            # Auto-decrypt on file upload
            file_input.upload(
                fn=read_uploaded_file, 
                inputs=file_input, 
                outputs=decrypt_input
            )
            
            # Auto-decrypt on file upload
            decrypt_input.change(
                fn=decrypt_message,
                inputs=[decrypt_input],
                outputs=decrypted_data_output
            )
            
            # Clear data when file is removed
            file_input.clear(
                lambda: [["", ""]], 
                None, 
                decrypted_data_output
            )

# Custom CSS for specific components (optional)
app.css = """
#encrypt-btn, #save-btn { background-color: #4CAF50; color: white; }
#decrypt-btn { background-color: #4CAF50; color: white; }
"""

# Launch the Gradio app
if __name__ == "__main__":
    app.launch()