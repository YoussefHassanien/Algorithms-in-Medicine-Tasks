import gradio as gr
import base64
import os

def encrypt_message(patient_name, age, gender, address, phone, emergency_contact, insurance, medical_history, diagnosis):
    # Validate input
    if not patient_name or not diagnosis:
        return "Please fill in all required fields"
    
    # Combine all patient information
    combined_message = (
        f"Name: {patient_name}; Age: {age}; Gender: {gender}; Address: {address}; "
        f"Phone: {phone}; Emergency Contact: {emergency_contact}; Insurance: {insurance}; "
        f"Medical History: {medical_history}; Diagnosis: {diagnosis}"
    )
    
    try:
        # Simple base64 encoding
        encrypted_message = base64.b64encode(combined_message.encode('utf-8')).decode('utf-8')
        
        # Ensure the directory exists
        os.makedirs('encrypted_files', exist_ok=True)
        
        # Save to a file with a unique name
        filename = os.path.join('encrypted_files', f'{patient_name.replace(" ", "_")}_encrypted.txt')
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(encrypted_message)
        
        return f"Encrypted data saved to {filename}"
    
    except Exception as e:
        return f"Error encrypting data: {str(e)}"

def decrypt_message(encrypted_file=None):
    if encrypted_file is None:
        return []

    try:
        # Extract the actual file path from the temporary file wrapper
        file_path = encrypted_file.name if hasattr(encrypted_file, 'name') else encrypted_file
        
        # Read the encrypted file
        with open(file_path, 'r', encoding='utf-8') as f:
            encrypted_message = f.read().strip()
        
        # Decode the base64 message
        decrypted_message = base64.b64decode(encrypted_message).decode('utf-8')
        
        # Split the decrypted message into fields
        fields = [field.strip() for field in decrypted_message.split(';') if field]
        data = [[field.split(':')[0].strip(), field.split(':')[1].strip()] for field in fields]
        
        return data
    
    except Exception as e:
        return [["Error", str(e)]]

# Custom CSS for modern styling and enhanced color scheme
css = """
/* Global Styles */
# Encrypt Data, # Decrypt Data {
    background-color: #ffffff;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
}

/* Page background and main layout */
body {
    background-color: #f4f8f9;
    font-family: 'Arial', sans-serif;
    color: #333;
}

/* Title */
h1 {
    font-size: 2.5rem;
    color: #005F73;
    text-align: center;
    margin-bottom: 30px;
    font-weight: 700;
}

/* Custom button styling */
.gradio-button {
    background-color: #2a9d8f; /* Teal */
    color: white;
    font-weight: bold;
    border-radius: 8px;
    padding: 12px 24px;
    font-size: 16px;
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
    transition: background-color 0.3s ease, transform 0.2s;
}

.gradio-button:hover {
    background-color: #21867a; /* Darker Teal */
    transform: translateY(-2px);
    cursor: pointer;
}

/* Custom input styling */
input, textarea {
    border: 2px solid #e1e1e1;
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 14px;
    margin-bottom: 12px;
    width: 100%;
    box-sizing: border-box;
    background-color: #f9f9f9;
    transition: border-color 0.3s ease;
}

input:focus, textarea:focus {
    border-color: #2a9d8f;
    outline: none;
    background-color: #ffffff;
}

/* Custom output styling */
#encrypt_output {
    color: #2a9d8f;
    font-size: 16px;
    font-weight: bold;
    margin-top: 10px;
    text-align: center;
}

/* Decrypted data output */
#decrypted_data_output {
    border: 2px solid #ddd; 
    background-color: #ffffff;
    color: #333;
    border-radius: 8px;
    padding: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    margin-top: 10px;
}

/* Tab styles */
.gr-tabs {
    background-color: #ffffff;
    border-radius: 12px;
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
}

.gr-tab {
    padding: 15px;
}

.gr-tab-button {
    background-color: #edf2f4;
    border: 2px solid #ccc;
    color: #333;
    font-weight: 600;
    font-size: 16px;
    padding: 8px 16px;
    border-radius: 6px;
}

.gr-tab-button:active {
    background-color: #d0d8e2;
}

/* Responsive Layouts */
@media (max-width: 768px) {
    h1 {
        font-size: 2rem;
    }

    .gr-row {
        flex-direction: column;
        align-items: center;
    }

    .gr-column {
        width: 100%;
    }
}
"""

# Create Gradio interface
with gr.Blocks(title="Simple Hospital Encryption Tool", css=css) as app:
    # Add title with custom colors and modern style
    gr.Markdown("<h1>Simple Hospital Encryption Tool</h1>")
    
    with gr.Tabs():
        # Encryption Tab
        with gr.Tab("Encrypt Data"):
            with gr.Row():
                with gr.Column():
                    patient_name = gr.Textbox(label="Patient Name", elem_id="patient_name")
                    age = gr.Number(label="Age")
                    gender = gr.Radio(choices=["Male", "Female"], label="Gender")
                    address = gr.Textbox(label="Address")
                with gr.Column():
                    phone = gr.Textbox(label="Phone Number")
                    emergency_contact = gr.Textbox(label="Emergency Contact")
                    insurance = gr.Textbox(label="Insurance Provider")
                    medical_history = gr.Textbox(label="Medical History")
            
            diagnosis = gr.Textbox(label="Diagnosis", lines=2, elem_id="diagnosis")
            encrypt_button = gr.Button("🔒 Encrypt Data", elem_classes=["gr-button-icon"])
            encrypt_output = gr.Textbox(label="Encryption Status", elem_id="encrypt_output")
            
            encrypt_button.click(
                fn=encrypt_message,
                inputs=[patient_name, age, gender, address, phone, emergency_contact, insurance, medical_history, diagnosis],
                outputs=encrypt_output
            )

        # Decryption Tab
        with gr.Tab("Decrypt Data"):
            decrypt_input = gr.File(label="Upload Encrypted File")
            decrypt_button = gr.Button("🔓 Decrypt Data", elem_classes=["gr-button-icon"])
            decrypted_data_output = gr.Dataframe(
                headers=["Field", "Value"], 
                datatype=["str", "str"], 
                label="Decrypted Registration Data", elem_id="decrypted_data_output"
            )
            
            decrypt_button.click(
                fn=decrypt_message,
                inputs=[decrypt_input],
                outputs=decrypted_data_output
            )

# Launch the app
if __name__ == "__main__":
    app.launch()
