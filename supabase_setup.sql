-- SQL queries for setting up the Supabase database tables for the AI Teaching Assistant Platform

-- Create schools table
CREATE TABLE schools (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    subscription_tier TEXT DEFAULT 'basic',
    max_users INTEGER DEFAULT 10,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create users table (linked to Supabase auth)
CREATE TABLE users (
    id UUID PRIMARY KEY REFERENCES auth.users,
    email TEXT NOT NULL UNIQUE,
    full_name TEXT,
    school_id UUID REFERENCES schools(id),
    role TEXT DEFAULT 'teacher',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

-- Create assistants table
CREATE TABLE assistants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    name TEXT NOT NULL,
    description TEXT,
    openai_assistant_id TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used TIMESTAMP WITH TIME ZONE
);

-- Create documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    assistant_id UUID REFERENCES assistants(id),
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    openai_file_id TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    file_url TEXT NOT NULL,
    status TEXT DEFAULT 'processing',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create chat_threads table
CREATE TABLE chat_threads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assistant_id UUID NOT NULL REFERENCES assistants(id),
    user_id UUID NOT NULL REFERENCES users(id),
    name TEXT,
    openai_thread_id TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_message_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create chat_messages table
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    thread_id UUID NOT NULL REFERENCES chat_threads(id),
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create vector_stores table
CREATE TABLE vector_stores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assistant_id UUID NOT NULL REFERENCES assistants(id),
    openai_vector_store_id TEXT NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_assistants_user_id ON assistants(user_id);
CREATE INDEX idx_documents_assistant_id ON documents(assistant_id);
CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_chat_threads_assistant_id ON chat_threads(assistant_id);
CREATE INDEX idx_chat_threads_user_id ON chat_threads(user_id);
CREATE INDEX idx_chat_messages_thread_id ON chat_messages(thread_id);
CREATE INDEX idx_vector_stores_assistant_id ON vector_stores(assistant_id);

-- Enable Row Level Security (RLS) policies
ALTER TABLE schools ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE assistants ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_threads ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE vector_stores ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Enable all operations for authenticated users" ON assistants
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Enable all operations for authenticated users" ON documents
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Enable all operations for authenticated users" ON chat_threads
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Enable all operations for authenticated users" ON chat_messages
    USING (EXISTS (
        SELECT 1 FROM chat_threads
        WHERE chat_threads.id = chat_messages.thread_id
        AND chat_threads.user_id = auth.uid()
    ))
    WITH CHECK (EXISTS (
        SELECT 1 FROM chat_threads
        WHERE chat_threads.id = chat_messages.thread_id
        AND chat_threads.user_id = auth.uid()
    ));

CREATE POLICY "Enable all operations for authenticated users" ON vector_stores
    USING (EXISTS (
        SELECT 1 FROM assistants
        WHERE assistants.id = vector_stores.assistant_id
        AND assistants.user_id = auth.uid()
    ))
    WITH CHECK (EXISTS (
        SELECT 1 FROM assistants
        WHERE assistants.id = vector_stores.assistant_id
        AND assistants.user_id = auth.uid()
    ));
