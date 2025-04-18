import streamlit as st
import time
import os
from dotenv import load_dotenv
import json
import random
from datetime import datetime

# Optional imports with error handling
try:
    from autogen import ConversableAgent, config_list_from_dotenv
    AUTOGEN_AVAILABLE = True
except ImportError:
    AUTOGEN_AVAILABLE = False

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Dialogue Generator",
    page_icon="💬",
    layout="wide"
)

# Custom CSS for chat bubbles
st.markdown("""
<style>
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 20px;
}
.chat-bubble {
    padding: 10px 15px;
    border-radius: 15px;
    max-width: 80%;
    margin: 5px 0;
}
.character1-bubble {
    background-color: #E5E5EA;
    color: black;
    align-self: flex-start;
    border-top-left-radius: 5px;
}
.character2-bubble {
    background-color: #007AFF;
    color: white;
    align-self: flex-end;
    border-top-right-radius: 5px;
    margin-left: auto;
}
.chat-name {
    font-size: 12px;
    margin-bottom: 2px;
    font-weight: bold;
}
.character1-name {
    color: #666;
}
.character2-name {
    color: #0056b3;
    text-align: right;
}
.stAlert {
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

def initialize_model_config():
    """Initialize model configuration from environment variables."""
    if not AUTOGEN_AVAILABLE:
        return None
        
    # Configure model API key map with multiple options
    model_api_key_map = {
        "llama3-70b-8192": {
            "api_key_env_var": "GROQ_API",
            "api_type": "groq",
        },
        "gpt-3.5-turbo": {
            "api_key_env_var": "OPENAI_API_KEY",
            "api_type": "openai",
        },
        "claude-3-sonnet-20240229": {
            "api_key_env_var": "ANTHROPIC_API_KEY",
            "api_type": "anthropic",
        }
    }
    
    # Get configuration from environment variables
    try:
        config_list = config_list_from_dotenv(
            dotenv_file_path=".env",
            model_api_key_map=model_api_key_map,
        )
        return config_list[0] if config_list else None
    except Exception as e:
        st.error(f"Error initializing model configuration: {str(e)}")
        return None

def generate_dialogue_with_autogen(character1_name, character2_name, situation, max_turns, model_config):
    """Generate a dialogue between two characters with a maximum number of turns using AutoGen."""
    if not model_config:
        return None
    
    # Initialize turn counter
    turn_counter = {"count": 0, "max": max_turns}
    
    # Define the termination function based on max turns
    def is_max_turns_reached(msg):
        turn_counter["count"] += 1
        return turn_counter["count"] >= turn_counter["max"]
    
    # System message for character 1
    character1_system_message = (
        f"You are {character1_name}. You are in the following situation: {situation}. "
        f"Your goal is to have a realistic conversation with {character2_name} "
        f"that addresses the situation naturally. Keep your responses concise and focused on the dialogue."
    )
    
    # System message for character 2
    character2_system_message = (
        f"You are {character2_name}. You are in the following situation: {situation}. "
        f"Your goal is to have a realistic conversation with {character1_name} "
        f"that addresses the situation naturally. Keep your responses concise and focused on the dialogue."
    )
    
    try:
        # Create character 1 agent
        character1 = ConversableAgent(
            name=character1_name,
            system_message=character1_system_message,
            llm_config=model_config,
            human_input_mode="NEVER",
        )
        
        # Create character 2 agent
        character2 = ConversableAgent(
            name=character2_name,
            system_message=character2_system_message,
            llm_config=model_config,
            human_input_mode="NEVER",
            is_termination_msg=is_max_turns_reached
        )
        
        # Generate an appropriate starter message based on the characters and situation
        starter_agent = ConversableAgent(
            name="starter_helper",
            system_message=(
                f"You are an assistant that generates the first line of dialogue for {character1_name} "
                f"to say to {character2_name} in this situation: {situation}. "
                f"Provide only the dialogue line, nothing else. Keep it concise and natural."
            ),
            llm_config=model_config,
            human_input_mode="NEVER",
        )
        
        with st.spinner("Generating dialogue starter..."):
            # Get the starter message
            starter_message = starter_agent.generate_reply(
                messages=[{"role": "user", "content": f"Generate the first line of dialogue for {character1_name}."}]
            )
        
        # Initiate the dialogue
        with st.spinner("Generating dialogue..."):
            chat_result = character1.initiate_chat(
                recipient=character2,
                message=starter_message,
            )
        
        return chat_result
    
    except Exception as e:
        st.error(f"Error generating dialogue: {str(e)}")
        return None

def generate_dialogue_fallback(character1_name, character2_name, situation, max_turns):
    """Generate a dialogue directly when AutoGen is not available or fails."""
    # Create a fallback dialogue without relying on external APIs
    messages = []
    
    # Create a basic starter message
    starter_options = [
        f"Hello {character2_name}, I wanted to talk about {situation.split()[0]}...",
        f"Hey {character2_name}, do you have a moment? I need to discuss {situation.split()[0]}.",
        f"Hi {character2_name}! I've been thinking about {situation.split()[0]}."
    ]
    
    messages.append({
        "role": "assistant", 
        "name": character1_name, 
        "content": random.choice(starter_options)
    })
    
    # Add a note that this is a placeholder dialogue
    messages.append({
        "role": "system",
        "content": "This is a placeholder dialogue. To generate real dialogues, please configure your API keys properly."
    })
    
    # Create a simple response
    messages.append({
        "role": "assistant",
        "name": character2_name,
        "content": f"Hi {character1_name}! Sure, what about {situation.split()[0]} did you want to discuss?"
    })
    
    # Add another exchange
    messages.append({
        "role": "assistant",
        "name": character1_name,
        "content": f"Well, regarding {situation}, I was hoping we could work through it together."
    })
    
    # Return a dummy dialogue result
    return {"messages": messages}

def generate_dialogue(character1_name, character2_name, situation, max_turns, model_config):
    """Generate dialogue using available methods."""
    # Try using AutoGen first if available
    if AUTOGEN_AVAILABLE and model_config:
        try:
            dialogue = generate_dialogue_with_autogen(
                character1_name, character2_name, situation, max_turns, model_config
            )
            if dialogue:
                return dialogue
        except Exception as e:
            st.warning(f"API Error: {str(e)}\n\nSwitching to fallback mode.")
    
    # If AutoGen fails or is not available, use the fallback
    return generate_dialogue_fallback(character1_name, character2_name, situation, max_turns)

def extract_messages(dialogue):
    """Extract messages from dialogue object regardless of its type."""
    # If dialogue is a dictionary with messages (fallback case)
    if isinstance(dialogue, dict) and "messages" in dialogue:
        return dialogue["messages"]
    # If dialogue is a ChatResult object from AutoGen
    elif hasattr(dialogue, "chat_history"):
        # Convert AutoGen ChatResult format to our expected format
        messages = []
        for entry in dialogue.chat_history:
            # AutoGen's chat_history is typically a list of dictionaries with {'name': ..., 'content': ...} structure
            if isinstance(entry, dict):
                sender_name = entry.get('name', 'Unknown')
                content = entry.get('content', '')
                messages.append({
                    "role": "assistant", 
                    "name": sender_name, 
                    "content": content
                })
        return messages
    # Fallback for older AutoGen versions that might use 'messages' attribute
    elif hasattr(dialogue, "messages"):
        return dialogue.messages
    else:
        # For unknown formats, let's log some debug info
        if st.session_state.get("debug_mode", False):
            st.write(f"Unknown dialogue format: {type(dialogue)}")
            st.write(str(dialogue)[:500])  # Show first 500 chars to avoid overflow
        return []

def display_dialogue(dialogue, character1_name, character2_name):
    """Display the dialogue in a chat-like interface."""
    # Debug the dialogue object type and structure if debug mode is enabled
    if st.session_state.get("debug_mode", False):
        st.write(f"Dialogue type: {type(dialogue)}")
        
        if hasattr(dialogue, "chat_history"):
            st.write("Chat history available")
            # Display the first 5 entries to avoid overwhelming the UI
            st.write("First few entries:")
            for i, entry in enumerate(dialogue.chat_history[:5]):
                st.write(f"Entry {i}: {entry}")
        
        if hasattr(dialogue, "__dict__"):
            st.write("Dialogue attributes:")
            for attr in dir(dialogue):
                if not attr.startswith("_") and not callable(getattr(dialogue, attr)):
                    st.write(f"{attr}: {getattr(dialogue, attr)}")
    
    # Extract messages from dialogue object
    messages = extract_messages(dialogue)
    
    if not messages:
        st.warning("No dialogue generated or messages couldn't be extracted.")
        return
    
    st.markdown(f"### Dialogue between {character1_name} and {character2_name}")
    
    # Create a container for the chat messages
    chat_container = st.container()
    
    with chat_container:
        for message in messages:
            # Skip system messages unless in debug mode
            if message.get("role") == "system" and not st.session_state.get("debug_mode", False):
                continue
                
            # Determine which character is speaking
            if message.get("role") == "assistant":
                speaker = message.get("name", "Unknown")
                content = message.get("content", "")
            else:
                speaker = message.get("role", "Unknown")
                content = message.get("content", "")
            
            # Determine which CSS class to use based on the speaker
            if speaker == character1_name:
                name_class = "character1-name"
                bubble_class = "character1-bubble"
            elif speaker == character2_name:
                name_class = "character2-name"
                bubble_class = "character2-bubble"
            else:
                # For system messages or others
                name_class = "character1-name"
                bubble_class = "character1-bubble"
            
            # Display the message with the appropriate styling
            st.markdown(f"""
            <div class="chat-name {name_class}">{speaker}</div>
            <div class="chat-bubble {bubble_class}">{content}</div>
            """, unsafe_allow_html=True)
            
            # Add a small delay to create a chat-like appearance
            time.sleep(0.1)

def save_dialogue_to_file(dialogue, character1_name, character2_name, situation):
    """Save the dialogue to a JSON file."""
    if not os.path.exists("saved_dialogues"):
        os.makedirs("saved_dialogues")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"saved_dialogues/dialogue_{character1_name}_{character2_name}_{timestamp}.json"
    
    # Extract messages from dialogue object
    messages = extract_messages(dialogue)
    
    data = {
        "character1": character1_name,
        "character2": character2_name,
        "situation": situation,
        "timestamp": datetime.now().isoformat(),
        "messages": messages
    }
    
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    
    return filename

def format_dialogue_text(dialogue, character1_name, character2_name, situation):
    """Format the dialogue as downloadable text."""
    text = f"Dialogue between {character1_name} and {character2_name}\n"
    text += f"Situation: {situation}\n\n"
    
    # Extract messages from dialogue object
    messages = extract_messages(dialogue)
    
    for message in messages:
        # Skip system messages
        if message.get("role") == "system":
            continue
            
        if message.get("role") == "assistant":
            speaker = message.get("name", "Unknown")
        else:
            speaker = message.get("role", "Unknown")
        
        text += f"{speaker}: {message.get('content', '')}\n\n"
    
    return text

def main():
    # Initialize session state
    if "dialogue_history" not in st.session_state:
        st.session_state.dialogue_history = {}
    
    if "debug_mode" not in st.session_state:
        st.session_state.debug_mode = False
    
    # Toggle for debug mode (hidden in the UI by default)
    if st.sidebar.checkbox("Enable Debug Mode", value=st.session_state.debug_mode, key="debug_checkbox"):
        st.session_state.debug_mode = True
    else:
        st.session_state.debug_mode = False
    
    # Display API status
    model_config = initialize_model_config()
    
    if st.session_state.debug_mode:
        if AUTOGEN_AVAILABLE:
            st.sidebar.success("AutoGen is available.")
            if model_config:
                st.sidebar.success("API configuration loaded successfully.")
            else:
                st.sidebar.warning("API configuration failed to load. Check your .env file.")
        else:
            st.sidebar.error("AutoGen is not installed. Running in fallback mode.")
    
    st.title("AI Dialogue Generator")
    st.markdown("Generate realistic dialogues between characters in specific situations")
    
    # Create tabs for different options
    tab1, tab2 = st.tabs(["Generate New Dialogue", "About"])
    
    with tab1:
        # Input form for dialogue parameters
        with st.form("dialogue_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                character1_name = st.text_input("Character 1 Name", "Teacher")
                situation = st.text_area("Situation", "The teacher is helping the student understand and solve Fibonacci sequence problems.")
            
            with col2:
                character2_name = st.text_input("Character 2 Name", "Student")
                max_turns = st.number_input("Maximum Dialogue Turns", min_value=1, max_value=30, value=5, step=1, 
                                           help="The dialogue will stop after this many turns")
            
            generate_button = st.form_submit_button("Generate Dialogue")
        
        # Generate dialogue when the button is clicked
        if generate_button:
            if not character1_name or not character2_name or not situation:
                st.error("Please fill in all required fields.")
            else:
                # Generate and display the dialogue
                dialogue = generate_dialogue(
                    character1_name, 
                    character2_name, 
                    situation,
                    max_turns,
                    model_config
                )
                
                if dialogue:
                    # Store in session state with a unique key
                    dialogue_key = f"{character1_name}_{character2_name}_{int(time.time())}"
                    st.session_state.dialogue_history[dialogue_key] = {
                        "dialogue": dialogue,
                        "character1": character1_name,
                        "character2": character2_name,
                        "situation": situation,
                        "max_turns": max_turns
                    }
                    
                    # Display the dialogue
                    display_dialogue(dialogue, character1_name, character2_name)
                    
                    # Export options
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.download_button(
                            label="Download as Text",
                            data=format_dialogue_text(dialogue, character1_name, character2_name, situation),
                            file_name=f"dialogue_{character1_name}_{character2_name}.txt",
                            mime="text/plain"
                        )
                    
                    with col2:
                        if st.button("Save Dialogue to File"):
                            filename = save_dialogue_to_file(dialogue, character1_name, character2_name, situation)
                            st.success(f"Dialogue saved to {filename}")
    
    with tab2:
        st.markdown("""
        ## About Dialogue Generator
        
        This application generates realistic dialogues between two characters in a specific situation.
        
        ### Features:
        - Specify character names and their situation
        - Set a maximum number of dialogue turns
        - Download generated dialogues as text files
        - Save dialogues to local JSON files
        
        ### How to use:
        1. Enter names for both characters
        2. Describe the situation they're in
        3. Specify how many turns of dialogue you want
        4. Click "Generate Dialogue" and watch the conversation unfold!
        
        ### API Usage Notes:
        If you're encountering rate limit errors with Groq API, you can:
        - Wait until your quota resets (check error message for timing)
        - Consider upgrading to a higher tier for more tokens
        - Configure alternative API providers in the .env file
        
        ### Example scenarios:
        - Teacher and student solving math problems
        - Doctor and patient discussing treatment options
        - Job interviewer and candidate
        - Detective interrogating a suspect
        - Customer and service representative resolving an issue
        """)
        
        # Rate limit information
        st.subheader("API Rate Limits")
        st.markdown("""
        **Groq API** has a limit of 100,000 tokens per day on the free tier. If you hit this limit, you'll need to:
        1. Wait for your quota to reset (usually 24 hours)
        2. Upgrade to a higher tier at [Groq Console](https://console.groq.com/settings/billing)
        3. Use an alternative API provider
        
        To use alternative providers, add their API keys to your `.env` file:
        ```
        GROQ_API=your_groq_api_key
        OPENAI_API_KEY=your_openai_api_key
        ANTHROPIC_API_KEY=your_anthropic_api_key
        ```
        """)
        
        # Debug information (only shown in debug mode)
        if st.session_state.debug_mode:
            st.subheader("Debug Information")
            st.json({
                "autogen_available": AUTOGEN_AVAILABLE,
                "model_config": str(model_config) if model_config else "None",
                "dialogue_history_count": len(st.session_state.dialogue_history)
            })

if __name__ == "__main__":
    main()