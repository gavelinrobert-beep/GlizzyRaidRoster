class SignupCommand:
    def __init__(self):
        self.signups = []  # List to store player signups

    def signup(self, character_name, player_class, spec_role):
        # Create a player signup entry
        signup_entry = {
            'character_name': character_name,
            'class': player_class,
            'spec/role': spec_role
        }
        self.signups.append(signup_entry)
        return f'{character_name} has signed up for raids as a {player_class} ({spec_role}).'

    def get_signups(self):
        return self.signups

# Example usage:
# command = SignupCommand()
# print(command.signup('Thorin', 'Warrior', 'Tank'))
# print(command.get_signups())