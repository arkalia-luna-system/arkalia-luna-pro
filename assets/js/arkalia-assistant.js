document.addEventListener("DOMContentLoaded", function () {
    const btn = document.createElement("button");
    btn.textContent = "💬 Parler à Arkalia";
    btn.onclick = async () => {
        const message = prompt("Que veux-tu demander à Arkalia ?");
        const res = await fetch("http://localhost:8001/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message }),
        });
        const data = await res.json();
        alert("Réponse IA : " + data.response);
    };
    document.body.appendChild(btn);
});