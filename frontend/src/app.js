document.getElementById("searchBtn").addEventListener("click", async () => {
    const query = document.getElementById("queryInput").value;
    const loader = document.getElementById("loader");
    const resultContainer = document.getElementById("resultContainer");
    const responseText = document.getElementById("responseText");

    if (!query.trim()) return alert("Bara, enter a query first!");

    loader.classList.remove("hidden");
    resultContainer.classList.add("hidden");

    try {
        const data = await fetchSearchResults(query);

        
        if (data && data.answer) {
            responseText.innerText = data.answer;
        } 
        
        else if (data && data.status === "success") {
            responseText.innerText = data.answer || data.data;
        } 
        else {
            responseText.innerText = "Error: " + (data.message || "Failed to process response");
        }
    } catch (error) {
        responseText.innerText = "Error: " + error.message;
        console.error(error);
    } finally {
        loader.classList.add("hidden");
        resultContainer.classList.remove("hidden");
    }
});