# AI Teaching Assistant Platform

A Streamlit-based web application that enables educators to create personalized AI assistants powered by their own curriculum materials. The platform leverages OpenAI's Assistants API for AI capabilities and Supabase for authentication, database operations, and file storage.

## Core Features

- **Authentication**: Secure teacher login/signup system with profile management
- **Custom AI Assistants**: Create and configure AI assistants with specific instructions tailored to teaching needs
- **Document Management**: Upload, organize, and manage curriculum materials (PDFs, Word docs, text files)
- **Interactive Chat**: Clean, responsive chat interface with real-time AI responses
- **Chat History**: View, search, and manage previous conversations
- **Document Integration**: AI assistants can reference uploaded materials to provide contextually relevant responses

## Technical Stack

### Frontend
- **Streamlit**: Responsive web interface with minimal frontend code
- **UI Components**: Modular design for authentication, assistant management, and chat

### Backend
- **Python**: Core application logic and API integrations
- **OpenAI Assistants API**: AI capabilities powered by GPT-4 Turbo
- **Supabase**: Authentication, database operations, and file storage
- **Document Processing**: Support for PDF, DOCX, DOC, TXT, and MD files

## Project Structure

```
teachers-tutor/
├── app.py                  # Main Streamlit application entry point
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (gitignored)
├── config/
│   └── settings.py         # Configuration and environment variables
├── services/
│   ├── auth_service.py     # Authentication with Supabase
│   ├── database_service.py # Supabase database operations
│   ├── openai_service.py   # OpenAI API integration
│   └── document_service.py # Document handling and processing
├── models/
│   └── data_models.py      # Pydantic models for data validation
├── ui/
│   ├── auth_ui.py          # Authentication UI components
│   ├── assistant_ui.py     # Assistant management UI
│   └── chat_ui.py          # Chat interface UI
└── utils/
    └── logging_utils.py    # Logging utilities
```

## Setup and Installation

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/dgmulei/teachers-tutor.git
   cd teachers-tutor
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   SUPABASE_DB_PASSWORD=your_supabase_db_password
   APP_NAME="AI Teaching Assistant"
   DEBUG=True
   ```

5. Run the application:
   ```bash
   streamlit run app.py
   ```

### Deploying to Streamlit Cloud

1. Push your code to GitHub (already done if you're viewing this on GitHub)

2. Create a Streamlit account at https://streamlit.io/ if you don't have one

3. Create a new app in Streamlit Cloud:
   - Connect to your GitHub repository
   - Set the main file path to `app.py`
   - Set the Python version to 3.9 or higher

4. Set up the required secrets in the Streamlit Cloud dashboard:
   - Go to your app settings
   - Navigate to the "Secrets" section
   - Add the following secrets (use the template in `.streamlit/secrets_template.toml`):
     ```
     OPENAI_API_KEY = "your-openai-api-key"
     SUPABASE_URL = "your-supabase-url"
     SUPABASE_KEY = "your-supabase-key"
     SUPABASE_DB_PASSWORD = "your-supabase-db-password"
     APP_NAME = "AI Teaching Assistant"
     DEBUG = "False"
     ```

5. Deploy the app and access it via the provided URL

## Database Schema

The application uses Supabase with the following key tables:

- **schools**: Educational institutions with subscription tiers
- **users**: Teacher accounts linked to Supabase auth
- **assistants**: Custom AI assistants created by teachers
- **documents**: Uploaded curriculum materials
- **chat_threads**: Conversations with assistants
- **chat_messages**: Individual messages in conversations
- **vector_stores**: Vector embeddings of documents

## Security Features

- **Row Level Security (RLS)**: Database policies ensure users can only access their own data
- **Secure Authentication**: Leverages Supabase for robust user management
- **File Validation**: Strict file type and size validation for uploads
- **Environment Variables**: Sensitive configuration stored in environment variables

## File Handling

- **Supported Formats**: PDF, DOCX, DOC, TXT, MD
- **Size Limit**: 20MB per file
- **Processing**: Automatic text extraction and storage
- **Storage**: Files stored in Supabase storage with public URLs

## Chat Settings

- **Model**: GPT-4 Turbo (via OpenAI Assistants API)
- **Message Limit**: 100 messages per thread
- **Message Length**: 4000 characters maximum

## Development Status

This is a prototype demonstrating core functionality with:
- Working user interface
- Backend integration with OpenAI and Supabase
- Document processing and storage
- Real-time chat capabilities

## Future Enhancements

1. **Enhanced Document Processing**:
   - Support for more file types
   - Improved text extraction
   - Better semantic search

2. **UI/UX Improvements**:
   - Mobile-responsive design
   - Dark mode
   - Accessibility features

3. **Advanced Features**:
   - LMS integration
   - Analytics dashboard
   - Collaborative tools
   - Student access portal

4. **Enterprise Features**:
   - School-wide deployment
   - Advanced admin controls
   - Custom branding options

## License

This project is intended for demonstration purposes.
