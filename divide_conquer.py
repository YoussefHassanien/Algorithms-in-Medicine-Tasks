import gradio as gr
import random

original_depth = None
min_chunk_size = 5


def encrypt_chunk(chunk, shift):
    return ''.join(chr((ord(c) + shift) % 256) for c in chunk)

def decrypt_chunk(chunk, shift):
    return ''.join(chr((ord(c) - shift) % 256) for c in chunk)

def get_shift(index):
    # Example: Increment shift value by 1 for each chunk
    return 3 + index

def divide_and_conquer_encrypt(message, depth, index=0):
    global min_chunk_size
    if len(message) <= min_chunk_size or depth == 0:
        shift = get_shift(index)
        return encrypt_chunk(message, shift)
    
    mid = max(len(message) // 2, min_chunk_size)
    left = divide_and_conquer_encrypt(message[:mid], depth - 1, index)
    right = divide_and_conquer_encrypt(message[mid:], depth - 1, index + 1)
    
    return left + right

def divide_and_conquer_decrypt(message, depth, original_depth, index=0):
    global min_chunk_size
    if depth != original_depth:
        return ''.join(random.choice('0123456789ABCDEF') for _ in range(len(message)))
    if len(message) <= min_chunk_size or depth == 0:
        shift = get_shift(index)
        return decrypt_chunk(message, shift)
    
    mid = max(len(message) // 2, min_chunk_size)
    left = divide_and_conquer_decrypt(message[:mid], depth - 1, depth - 1, index)
    right = divide_and_conquer_decrypt(message[mid:], depth - 1, depth - 1, index + 1)
    
    return left + right

def encrypt_message(message, security_level):
    global original_depth
    if not message:
        return "Please enter a message"
    original_depth = security_level
    return divide_and_conquer_encrypt(message, security_level)

def decrypt_message(message, security_level):
    if not message:
        return "Please enter a message"
    return divide_and_conquer_decrypt(message, security_level, original_depth)

# Create Gradio interface
with gr.Blocks(title="Recursive Encryption/Decryption", theme=gr.themes.Soft()) as app:
    gr.Markdown("# Recursive Message Encryption and Decryption Tool")
    
    with gr.Tabs():
        with gr.Tab("Encrypt"):
            with gr.Row():
                encrypt_input = gr.Textbox(label="Enter message to encrypt")
                security_level = gr.Slider(minimum=1, maximum=5, value=3, step=1, 
                                           label="Security Level")
            encrypt_output = gr.Textbox(label="Encrypted message")
            encrypt_button = gr.Button("Encrypt")
            encrypt_button.click(
                fn=encrypt_message,
                inputs=[encrypt_input, security_level],
                outputs=encrypt_output
            )

        with gr.Tab("Decrypt"):
            with gr.Row():
                decrypt_input = gr.Textbox(label="Enter message to decrypt")
                security_level = gr.Slider(minimum=1, maximum=5, value=3, step=1, 
                                           label="Security Level")
            decrypt_output = gr.Textbox(label="Decrypted message")
            decrypt_button = gr.Button("Decrypt")
            decrypt_button.click(
                fn=decrypt_message,
                inputs=[decrypt_input, security_level],
                outputs=decrypt_output
            )

if __name__ == "__main__":
    app.launch()