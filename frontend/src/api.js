const API_BASE_URL = "https://d1oknu53oez56x.cloudfront.net";

async function fetchSearchResults(query) {
    const response = await fetch(`${API_BASE_URL}/api/search/`, {
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