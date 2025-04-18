from autogen import ConversableAgent, config_list_from_dotenv
import os
from dotenv import load_dotenv

class DialogueGenerator:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Configure model API key map
        self.model_api_key_map = {
            "llama-3.3-70b-versatile": {
                "api_key_env_var": "GROQ_API",
                "api_type": "groq",
            }
        }
        
        # Get configuration from environment variables
        self.config_list = config_list_from_dotenv(
            dotenv_file_path=".env",
            model_api_key_map=self.model_api_key_map,
        )
    
    def create_dialogue(self, character1_name, character2_name, situation, termination_condition):
        """
        Generate a dialogue between two characters in a given situation until termination condition is met.
        
        Args:
            character1_name (str): Name of the first character
            character2_name (str): Name of the second character
            situation (str): Description of the situation/context
            termination_condition (str): Condition that signals the end of the dialogue
        
        Returns:
            dict: The result of the conversation
        """
        # Define the termination function
        def is_termination_msg(msg):
            return termination_condition.lower() in msg["content"].lower()
        
        # Create the first character agent
        character1 = ConversableAgent(
            name=character1_name,
            system_message=f"You are {character1_name}. You are in the following situation: {situation}. "
                          f"Your goal is to have a realistic conversation with {character2_name} "
                          f"that addresses the situation naturally.",
            llm_config=self.config_list[0],
            human_input_mode="NEVER",
        )
        
        # Create the second character agent
        character2 = ConversableAgent(
            name=character2_name,
            system_message=f"You are {character2_name}. You are in the following situation: {situation}. "
                          f"Your goal is to have a realistic conversation with {character1_name} "
                          f"that addresses the situation naturally.",
            llm_config=self.config_list[0],
            human_input_mode="NEVER",
            is_termination_msg=is_termination_msg
        )
        
        # Determine which character should start the conversation based on the situation
        starter_message = self._generate_starter_message(character1_name, character2_name, situation)
        
        # Initiate the dialogue
        chat_result = character1.initiate_chat(
            recipient=character2,
            message=starter_message,
        )
        
        return chat_result
    
    def _generate_starter_message(self, character1_name, character2_name, situation):
        """Generate an appropriate starter message based on the situation"""
        # Create a helper agent to determine an appropriate first line
        starter_agent = ConversableAgent(
            name="starter_helper",
            system_message=f"You are an assistant that generates the first line of dialogue for {character1_name} "
                          f"to say to {character2_name} in this situation: {situation}. "
                          f"Provide only the dialogue line, nothing else.",
            llm_config=self.config_list[0],
            human_input_mode="NEVER",
        )
        
        # Get the starter message
        response = starter_agent.generate_reply(
            messages=[{"role": "user", "content": f"Generate the first line of dialogue for {character1_name}."}]
        )
        
        return response


def generate_specific_dialogue(character1_name, character2_name, situation, termination_condition):
    """
    Create a dialogue between specific characters in a given situation.
    This is a simplified version that doesn't use the DialogueGenerator class.
    
    Args:
        character1_name (str): Name of the first character
        character2_name (str): Name of the second character
        situation (str): Description of the situation/context
        termination_condition (str): Condition that signals the end of the dialogue
    
    Returns:
        dict: The result of the conversation
    """
    # Load environment variables
    load_dotenv()
    
    # Configure model API key map
    model_api_key_map = {
        "llama-3.3-70b-versatile": {
            "api_key_env_var": "GROQ_API",
            "api_type": "groq",
        }
    }
    
    # Get configuration from environment variables
    config_list = config_list_from_dotenv(
        dotenv_file_path=".env",
        model_api_key_map=model_api_key_map,
    )
    
    # Define the termination function
    def is_termination_msg(msg):
        return termination_condition.lower() in msg["content"].lower()
    
    # System message for character 1
    character1_system_message = (
        f"You are {character1_name}. You are in the following situation: {situation}. "
        f"Your goal is to have a realistic conversation with {character2_name} "
        f"that addresses the situation naturally."
    )
    
    # System message for character 2
    character2_system_message = (
        f"You are {character2_name}. You are in the following situation: {situation}. "
        f"Your goal is to have a realistic conversation with {character1_name} "
        f"that addresses the situation naturally."
    )
    
    # Create character 1 agent
    character1 = ConversableAgent(
        name=character1_name,
        system_message=character1_system_message,
        llm_config=config_list[0],
        human_input_mode="NEVER",
    )
    
    # Create character 2 agent
    character2 = ConversableAgent(
        name=character2_name,
        system_message=character2_system_message,
        llm_config=config_list[0],
        human_input_mode="NEVER",
        is_termination_msg=is_termination_msg
    )
    
    # Generate an appropriate starter message based on the characters and situation
    starter_agent = ConversableAgent(
        name="starter_helper",
        system_message=(
            f"You are an assistant that generates the first line of dialogue for {character1_name} "
            f"to say to {character2_name} in this situation: {situation}. "
            f"Provide only the dialogue line, nothing else."
        ),
        llm_config=config_list[0],
        human_input_mode="NEVER",
    )
    
    # Get the starter message
    starter_message = starter_agent.generate_reply(
        messages=[{"role": "user", "content": f"Generate the first line of dialogue for {character1_name}."}]
    )
    
    # Initiate the dialogue
    chat_result = character1.initiate_chat(
        recipient=character2,
        message=starter_message,
    )
    
    return chat_result


def generate_fibonacci_dialogue():
    """
    Generate a specific dialogue between a teacher and student about the Fibonacci sequence.
    """
    # Load environment variables
    load_dotenv()
    
    # Configure model API key map
    model_api_key_map = {
        "llama-3.3-70b-versatile": {
            "api_key_env_var": "GROQ_API",
            "api_type": "groq",
        }
    }
    
    # Get configuration from environment variables
    config_list = config_list_from_dotenv(
        dotenv_file_path=".env",
        model_api_key_map=model_api_key_map,
    )
    
    # Define teacher agent
    teacher = ConversableAgent(
        name="Teacher",
        system_message="You are a math teacher helping a student understand the Fibonacci sequence. "
                     "Your goal is to guide the student to understand and solve Fibonacci problems. "
                     "Explain concepts clearly and provide examples. Ask questions to check understanding. "
                     "Be patient and encouraging.",
        llm_config=config_list[0],
        human_input_mode="NEVER",
    )
    
    # Define student agent
    student = ConversableAgent(
        name="Student",
        system_message="You are a student learning about the Fibonacci sequence. "
                     "You're struggling to understand the concept but are eager to learn. "
                     "Ask questions when you don't understand. "
                     "When you finally understand how to solve Fibonacci problems, "
                     "say exactly 'I understand how to solve Fibonacci problems now! Thank you for your help.'",
        llm_config=config_list[0],
        human_input_mode="NEVER",
        is_termination_msg=lambda msg: "I understand how to solve Fibonacci problems now" in msg["content"]
    )
    
    # Start the conversation
    chat_result = teacher.initiate_chat(
        recipient=student,
        message="Today we're going to learn about the Fibonacci sequence. Have you heard of it before?",
    )
    
    return chat_result


def format_dialogue(dialogue):
    """Format the dialogue in a readable way"""
    formatted_dialogue = "\nFULL DIALOGUE:\n\n"
    
    for message in dialogue["messages"]:
        sender = message["role"] if message["role"] != "assistant" else message["name"]
        formatted_dialogue += f"{sender}: {message['content']}\n\n"
    
    return formatted_dialogue


def main():
    print("Dialogue Generator - Choose an option:")
    print("1. Use predefined Teacher-Student Fibonacci dialogue")
    print("2. Create a custom dialogue")
    
    choice = input("Enter your choice (1 or 2): ")
    
    if choice == "1":
        dialogue = generate_fibonacci_dialogue()
        print(format_dialogue(dialogue))
        
    elif choice == "2":
        character1 = input("Enter name for Character 1: ")
        character2 = input("Enter name for Character 2: ")
        situation = input("Enter the situation: ")
        termination = input("Enter the termination condition: ")
        
        generator = DialogueGenerator()
        dialogue = generator.create_dialogue(character1, character2, situation, termination)
        print(format_dialogue(dialogue))
        
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    main()