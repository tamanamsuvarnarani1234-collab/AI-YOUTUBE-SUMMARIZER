document.addEventListener("DOMContentLoaded", function () {

    const form = document.querySelector("form");
    const urlInput = document.querySelector(
        'input[name="youtube_url"]'
    );
    const transcriptInput = document.querySelector(
        'textarea[name="transcript"]'
    );
    const button = document.querySelector("button");

    form.addEventListener("submit", function (event) {

        const url = urlInput.value.trim();
        const transcript = transcriptInput.value.trim();

        if (url === "" && transcript === "") {
            event.preventDefault();
            alert("Please enter a YouTube URL or paste a transcript.");
            return;
        }

        button.textContent = "Generating Notes...";
        button.disabled = true;

    });

});
