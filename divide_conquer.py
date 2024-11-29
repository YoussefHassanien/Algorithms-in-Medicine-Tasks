import gradio as gr  # Import Gradio for creating the web interface
import random  # Import random for generating random values

# Global variables
original_depth = None  # Store the original depth for decryption verification
min_chunk_size = 5    # Minimum size of chunks for processing

def encrypt_chunk(chunk, shift):
    # Encrypt each character in the chunk by shifting its ASCII value
    # Use modulo 256 to keep values in valid ASCII range (0-255)
    return ''.join(chr((ord(c) + shift) % 256) for c in chunk)

def decrypt_chunk(chunk, shift):
    # Decrypt each character in the chunk by reverse shifting its ASCII value
    # Use modulo 256 to keep values in valid ASCII range (0-255)
    return ''.join(chr((ord(c) - shift) % 256) for c in chunk)

def get_shift(index):
    # Calculate shift value based on chunk index
    # Example: Each chunk gets a different shift value (3 + index)
    return 3 + index

def divide_and_conquer_encrypt(message, depth, index=0):
    global min_chunk_size
    # Base case: if message is small enough or reached minimum chunk size
    if len(message) <= min_chunk_size:
        # Apply encryption multiple times based on depth
        for i in range(depth - 1):
            shift = get_shift(index)
            encrypt_chunk(message, shift)
        return encrypt_chunk(message, shift)
    
    # Divide step: split message into two parts
    mid = max(len(message) // 2, min_chunk_size)
    # Conquer step: recursively encrypt each half
    left = divide_and_conquer_encrypt(message[:mid], depth, index)
    right = divide_and_conquer_encrypt(message[mid:], depth, index + 1)
    
    # Combine step: join encrypted halves
    return left + right

def divide_and_conquer_decrypt(message, depth, original_depth, index=0):
    global min_chunk_size
    # Security check: return random string if depth doesn't match
    if depth != original_depth:
        return ''.join(random.choice('0123456789ABCDEF') for _ in range(len(message)))
    
    # Base case: if message is small enough or reached minimum chunk size
    if len(message) <= min_chunk_size:
        # Apply decryption multiple times based on depth
        for i in range(depth - 1):
            shift = get_shift(index)
            decrypt_chunk(message, shift)
        return decrypt_chunk(message, shift)
    
    # Divide step: split message into two parts
    mid = max(len(message) // 2, min_chunk_size)
    # Conquer step: recursively decrypt each half
    left = divide_and_conquer_decrypt(message[:mid], depth, depth, index)
    right = divide_and_conquer_decrypt(message[mid:], depth, depth, index + 1)
    
    # Combine step: join decrypted halves
    return left + right

def encrypt_message(message, security_level):
    global original_depth
    # Input validation
    if not message:
        return "Please enter a message"
    # Store security level for later verification
    original_depth = security_level
    return divide_and_conquer_encrypt(message, security_level)

def decrypt_message(message, security_level):
    # Input validation
    if not message:
        return "Please enter a message"
    return divide_and_conquer_decrypt(message, security_level, original_depth)

# Create Gradio interface with encryption/decryption tabs
with gr.Blocks(title="Recursive Encryption/Decryption", theme=gr.themes.Soft()) as app:
    gr.Markdown("# Recursive Message Encryption and Decryption Tool")
    
    with gr.Tabs():
        # Encryption tab
        with gr.Tab("Encrypt"):
            with gr.Row():
                # Input fields for encryption
                encrypt_input = gr.Textbox(label="Enter message to encrypt")
                security_level = gr.Slider(minimum=1, maximum=5, value=3, step=1, 
                                           label="Security Level")
            encrypt_output = gr.Textbox(label="Encrypted message")
            encrypt_button = gr.Button("Encrypt")
            # Connect encryption function to button click
            encrypt_button.click(
                fn=encrypt_message,
                inputs=[encrypt_input, security_level],
                outputs=encrypt_output
            )

        # Decryption tab
        with gr.Tab("Decrypt"):
            with gr.Row():
                # Input fields for decryption
                decrypt_input = gr.Textbox(label="Enter message to decrypt")
                security_level = gr.Slider(minimum=1, maximum=5, value=3, step=1, 
                                           label="Security Level")
            decrypt_output = gr.Textbox(label="Decrypted message")
            decrypt_button = gr.Button("Decrypt")
            # Connect decryption function to button click
            decrypt_button.click(
                fn=decrypt_message,
                inputs=[decrypt_input, security_level],
                outputs=decrypt_output
            )

# Launch the Gradio app when script is run directly
if __name__ == "__main__":
    app.launch()