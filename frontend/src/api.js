const API_BASE_URL = "http://localhost:8002/api";

async function fetchSearchResults(query) {
    const response = await fetch(`${API_BASE_URL}/search/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: query }),
    });
    
    if (!response.ok) {
        throw new Error("Network response was not ok");
    }
    
    return await response.json();
}