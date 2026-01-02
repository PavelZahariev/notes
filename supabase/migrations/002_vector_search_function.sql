-- Create function for vector similarity search
-- This function enables semantic search across entries using embeddings

CREATE OR REPLACE FUNCTION search_similar_entries(
    user_id_param UUID,
    query_embedding vector(1536),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    user_id UUID,
    content TEXT,
    summary TEXT,
    intent intent_type,
    category TEXT,
    created_at TIMESTAMPTZ,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.id,
        e.user_id,
        e.content,
        e.summary,
        e.intent,
        e.category,
        e.created_at,
        1 - (e.embedding <=> query_embedding) AS similarity
    FROM entries e
    WHERE 
        e.user_id = user_id_param
        AND e.embedding IS NOT NULL
        AND (1 - (e.embedding <=> query_embedding)) >= match_threshold
    ORDER BY e.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION search_similar_entries(UUID, vector(1536), FLOAT, INT) TO authenticated;

