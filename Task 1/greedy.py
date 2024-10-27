import gradio as gr
import pandas as pd

class Drug:
    def __init__(self, name, benefit_per_unit, cost_per_unit, side_effect_per_unit, max_quantity):
        self.name = name
        self.benefit_per_unit = benefit_per_unit
        self.cost_per_unit = cost_per_unit
        self.side_effect_per_unit = side_effect_per_unit
        self.max_quantity = max_quantity

def greedy_drug_selection_with_target(drugs, budget, side_effect_limit, target_benefit):
    drugs = sorted(drugs, key=lambda x: x.benefit_per_unit / x.cost_per_unit, reverse=True)
    
    selected_drugs = []
    total_benefit = 0
    total_cost = 0
    total_side_effect = 0
    
    for drug in drugs:
        for quantity in range(1, drug.max_quantity + 1):
            if (total_cost + drug.cost_per_unit <= budget and 
                total_side_effect + drug.side_effect_per_unit <= side_effect_limit and 
                total_benefit + drug.benefit_per_unit <= target_benefit):
                
                selected_drugs.append((drug.name, quantity))
                total_benefit += drug.benefit_per_unit
                total_cost += drug.cost_per_unit
                total_side_effect += drug.side_effect_per_unit
                
                if total_benefit >= target_benefit:
                    return selected_drugs, total_benefit, total_cost, total_side_effect
            else:
                break
                
    return selected_drugs, total_benefit, total_cost, total_side_effect

class DrugSelector:
    def __init__(self):
        self.drugs = []
        
    def add_drug(self, name, benefit, cost, side_effect, max_quantity):
        try:
            if not name or not benefit or not cost or not side_effect or not max_quantity:
                return None
                
            drug = Drug(
                name=name,
                benefit_per_unit=float(benefit),
                cost_per_unit=float(cost),
                side_effect_per_unit=float(side_effect),
                max_quantity=int(max_quantity)
            )
            self.drugs.append(drug)
            
            # Create DataFrame of current drugs
            drug_data = {
                'Name': [d.name for d in self.drugs],
                'Benefit': [d.benefit_per_unit for d in self.drugs],
                'Cost': [d.cost_per_unit for d in self.drugs],
                'Side Effect': [d.side_effect_per_unit for d in self.drugs],
                'Max Quantity': [d.max_quantity for d in self.drugs]
            }
            df = pd.DataFrame(drug_data)
            
            return df
        except ValueError:
            return None
    
    def calculate_selection(self, budget, side_effect_limit, target_benefit):
        try:
            budget = float(budget)
            side_effect_limit = float(side_effect_limit)
            target_benefit = float(target_benefit)
            
            if not self.drugs:
                return "Please add some drugs first.", None
            
            selected_drugs, total_benefit, total_cost, total_side_effect = greedy_drug_selection_with_target(
                self.drugs, budget, side_effect_limit, target_benefit
            )
            
            # Create optimized summary with selected drugs
            if selected_drugs:
                # Create a dictionary to combine quantities for same drugs
                drug_quantities = {}
                for drug, qty in selected_drugs:
                    if drug in drug_quantities:
                        drug_quantities[drug] += qty
                    else:
                        drug_quantities[drug] = qty
                
                # Create concise summary
                drug_summary = "\n".join([
                    f"💊 {drug}: {qty} units"
                    for drug, qty in drug_quantities.items()
                ])
                
                summary = f"""
Selected Drugs:
{drug_summary}

Summary:
✨ Total Benefit: {total_benefit:.2f}
💰 Total Cost: {total_cost:.2f}
⚠️ Total Side Effect: {total_side_effect:.2f}
                """
                
                # Create optimized DataFrame
                results_data = {
                    'Drug': list(drug_quantities.keys()),
                    'Quantity': list(drug_quantities.values())
                }
                results_df = pd.DataFrame(results_data)
                
                return summary, results_df
            else:
                return "No viable drug combination found.", None
                
        except ValueError:
            return "Error: Please ensure all constraints are valid numbers.", None

    def clear_drugs(self):
        self.drugs = []
        return None

# Create custom theme
custom_theme = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="indigo",
).set(
    button_primary_background_fill="*primary_500",
    button_primary_background_fill_hover="*primary_600",
    button_secondary_background_fill="*secondary_500",
    button_secondary_background_fill_hover="*secondary_600",
)

# Create the Gradio interface
drug_selector = DrugSelector()

with gr.Blocks(title="Medical Drug Selection", theme=custom_theme) as iface:
    gr.Markdown("""
    # 💊 Medical Drug Selection System
    
    Optimize drug selection based on benefits, costs, and side effects.
    """)
    
    with gr.Tab("📝 Add Drugs"):
        with gr.Row():
            with gr.Column(scale=1):
                name_input = gr.Textbox(
                    label="Drug Name",
                    placeholder="Enter drug name",
                )
                benefit_input = gr.Number(
                    label="Benefit per Unit"
                )
                cost_input = gr.Number(
                    label="Cost per Unit"
                )
                side_effect_input = gr.Number(
                    label="Side Effect per Unit"
                )
                max_quantity_input = gr.Number(
                    label="Max Quantity",
                    precision=0
                )
                
                with gr.Row():
                    add_btn = gr.Button("➕ Add Drug", variant="primary")
                    clear_btn = gr.Button("🗑️ Clear All", variant="secondary")
            
            with gr.Column(scale=2):
                drugs_table = gr.Dataframe(
                    headers=["Name", "Benefit", "Cost", "Side Effect", "Max Quantity"],
                    label="Current Drugs",
                    interactive=False
                )
    
    with gr.Tab("🔍 Calculate Selection"):
        with gr.Row():
            with gr.Column(scale=1):
                budget_input = gr.Number(
                    label="Budget"
                )
                side_effect_limit_input = gr.Number(
                    label="Side Effect Limit"
                )
                target_benefit_input = gr.Number(
                    label="Target Benefit"
                )
                
                calc_btn = gr.Button("🎯 Calculate Optimal Selection", variant="primary", size="lg")
            
            with gr.Column(scale=2):
                results_text = gr.Textbox(
                    label="Results Summary",
                    lines=6
                )
                results_table = gr.Dataframe(
                    headers=["Drug", "Quantity"],
                    label="Selected Drugs",
                    interactive=False
                )
    
    # Event handlers
    add_btn.click(
        drug_selector.add_drug,
        inputs=[name_input, benefit_input, cost_input, side_effect_input, max_quantity_input],
        outputs=[drugs_table]
    )
    
    clear_btn.click(
        drug_selector.clear_drugs,
        outputs=[drugs_table]
    )
    
    calc_btn.click(
        drug_selector.calculate_selection,
        inputs=[budget_input, side_effect_limit_input, target_benefit_input],
        outputs=[results_text, results_table]
    )

if __name__ == "__main__":
    iface.launch()