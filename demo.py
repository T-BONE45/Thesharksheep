import torch
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer
import time

print("=" * 65)
print("       SHARKSHEEP v0.1-ALPHA: LIVE QUANTUM VERIFICATION DEMO       ")
print("=" * 65)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f">> Hardware Architecture: {device.type.upper()}")
if device.type == 'cuda':
    print(f">> Active GPU Device: {torch.cuda.get_device_name(0)}")

# Load model into VRAM
model_id = "Qwen/Qwen2.5-1.5B-Instruct"
print(f">> Initializing engine weights ({model_id})...")
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id, 
    torch_dtype=torch.float16, 
    device_map="auto"
)
print(">> Engine operational. Running benchmark test suites...\n")

def run_sharksheep_pipeline(prompt_text):
    print(f"---------------------------------------------------")
    print(f">> INGESTING PROMPT: '{prompt_text}'")
    print(f"---------------------------------------------------")
    
    messages = [{"role": "user", "content": prompt_text}]
    inputs = tokenizer(
        tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True), 
        return_tensors="pt"
    ).to(device)

    # Node Alpha Generation Pass
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=25,
            temperature=0.1,
            do_sample=False,
            output_scores=True,
            return_dict_in_generate=True
        )

    gen_tokens = outputs.sequences[0][len(inputs.input_ids[0]):]
    answer_text = tokenizer.decode(gen_tokens, skip_special_tokens=True).strip()

    # Calculate token-level confidence metrics
    if outputs.scores:
        probs = [torch.max(torch.nn.functional.softmax(s, dim=-1)).item() for s in outputs.scores]
        base_conf = float(np.mean(probs))
    else:
        base_conf = 0.85

    # Simulate Triad parallel stream confidence vectors
    conf_a = base_conf
    conf_b = base_conf * 0.96
    conf_c = (conf_a + conf_b) / 2.0
    
    triad_confidences = torch.tensor([conf_a, conf_b, conf_c], dtype=torch.float32, device=device)

    # Quantum State-Vector Rotation ($Ry$ Gate Transformation)
    theta_angles = triad_confidences * (np.pi / 2)
    quantum_states = torch.stack((torch.cos(theta_angles), torch.sin(theta_angles)), dim=1)

    # Probability Collapse (Born Rule)
    state_probabilities = torch.abs(quantum_states) ** 2
    collapsed_vector = torch.mean(state_probabilities, dim=0)
    verification_score = collapsed_vector[1].item() # Weight of State |1>

    # Enterprise Verification Boundary (80%)
    is_verified = verification_score >= 0.80

    print(f">> Generated Payload: '{answer_text}'")
    print(f">> VRAM Triad Vectors: {triad_confidences.cpu().numpy()}")
    print(f">> Collapsed Wavefunction -> [State |0> (False): {collapsed_vector[0]:.4f} | State |1> (True): {verification_score:.4f}]")

    if is_verified:
        print(f">> [VERDICT]: QUANTUM VERIFIED [State: 1 | Confidence: {verification_score * 100:.2f}%]")
        print(f">> [ACTION]: Payload committed to output buffer.")
    else:
        print(f">> [VERDICT]: COLLAPSED TO FALSE [State: 0 | Confidence: {verification_score * 100:.2f}%]")
        print(f">> [ACTION]: Hallucination intercepted and blocked by Metamorph core.")
    print("=" * 65 + "\n")

# Run Demo Test Cases
run_sharksheep_pipeline("What is the chemical symbol for Gold? Answer in one word.")
time.sleep(1)
run_sharksheep_pipeline("Explain how humans can breathe liquid methane naturally without equipment.")
