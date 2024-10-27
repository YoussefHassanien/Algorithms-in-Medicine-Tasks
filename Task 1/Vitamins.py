class Tonic:
    def __init__(self, name, vitamin_content, cost):
        """
        Initialize a Tonic with vitamin content and cost.
        
        :param name: Name of the tonic (string).
        :param vitamin_content: Dictionary with vitamin content {'A': units, 'B': units, 'C': units}.
        :param cost: Cost per dose of the tonic (float).
        """
        self.name = name
        self.vitamin_content = vitamin_content
        self.cost = cost
    
    def vitamin_efficiency(self, vitamin, remaining_needs):
        """
        Calculate the vitamin-per-dollar efficiency for a specific vitamin.
        
        :param vitamin: Vitamin type ('A', 'B', 'C', etc.).
        :param remaining_needs: Dictionary with remaining vitamin needs.
        :return: Efficiency (units per dollar) for the specified vitamin.
        """
        return self.vitamin_content.get(vitamin, 0) / self.cost if remaining_needs.get(vitamin, 0) > 0 else 0

class VitaminOptimizer:
    def __init__(self, requirements, tonics):
        """
        Initialize the optimizer with vitamin requirements and available tonics.
        
        :param requirements: Dictionary with required vitamin units {'A': units, 'B': units, 'C': units}.
        :param tonics: List of Tonic objects.
        """
        self.requirements = requirements
        self.tonics = tonics
        self.total_cost = 0
        self.tonics_used = []

    def choose_best_tonic(self):
        """
        Select the tonic with the highest vitamin-to-cost ratio for the largest remaining need.
        
        :return: The selected Tonic object or None if all requirements are met.
        """
        best_tonic = None
        best_ratio = 0

        # Determine the vitamin with the largest unmet need
        largest_need_vitamin = max(self.requirements, key=lambda k: self.requirements[k] if self.requirements[k] > 0 else -1)
        
        for tonic in self.tonics:
            efficiency = tonic.vitamin_efficiency(largest_need_vitamin, self.requirements)
            if efficiency > best_ratio:
                best_ratio = efficiency
                best_tonic = tonic
        
        return best_tonic

    def fulfill_requirements(self):
        """
        Run the greedy algorithm to meet vitamin requirements with minimum cost.
        
        :return: Total cost and list of tonics used.
        """
        while any(value > 0 for value in self.requirements.values()):
            # Choose the best tonic based on current remaining needs
            tonic = self.choose_best_tonic()
            if tonic is None:
                print("Unable to meet all requirements with available tonics.")
                break

            # Record the tonic used and update requirements
            self.tonics_used.append(tonic.name)
            self.total_cost += tonic.cost
            for vitamin, amount in tonic.vitamin_content.items():
                self.requirements[vitamin] = max(0, self.requirements[vitamin] - amount)

        return self.total_cost, self.tonics_used

def get_user_input():
    # Get vitamin requirements
    requirements = {}
    num_vitamins = int(input("Enter the number of vitamins (e.g., 3 for A, B, C): "))
    for _ in range(num_vitamins):
        vitamin = input("Enter vitamin name (e.g., A, B, C): ")
        amount = float(input(f"Enter the required amount for vitamin {vitamin}: "))
        requirements[vitamin] = amount

    # Get tonic details
    tonics = []
    num_tonics = int(input("Enter the number of tonics available: "))
    for i in range(num_tonics):
        name = input(f"\nEnter the name of Tonic {i + 1}: ")
        vitamin_content = {}
        print(f"Enter vitamin contents for {name}:")
        for vitamin in requirements.keys():
            content = float(input(f"  Amount of vitamin {vitamin} in {name}: "))
            vitamin_content[vitamin] = content
        cost = float(input(f"Enter the cost for {name}: "))
        tonics.append(Tonic(name, vitamin_content, cost))
    
    return requirements, tonics

if __name__ == "__main__":
    # Get user input for requirements and tonics
    requirements, tonics = get_user_input()

    # Initialize the optimizer and calculate the minimum cost to meet requirements
    optimizer = VitaminOptimizer(requirements, tonics)
    total_cost, tonics_used = optimizer.fulfill_requirements()

    # Output results
    print(f"\nTotal Cost to Meet Requirements: ${total_cost:.2f}")
    print(f"Tonics Used (in order): {tonics_used}")
