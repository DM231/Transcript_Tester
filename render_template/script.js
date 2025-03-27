function uploadFile() {
    let fileInput = document.getElementById("fileInput");
    let file = fileInput.files[0];
    let statusText = document.getElementById("status");
    let resultText = document.getElementById("result");

    if (!file) {
        statusText.innerText = "يرجى اختيار ملف PDF!";
        return;
    }

    let formData = new FormData();
    formData.append("file", file);

    statusText.innerText = "جارٍ رفع الملف...";

    fetch("http://127.0.0.1:5000/upload", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        statusText.innerText = "تم رفع الملف!";
        resultText.innerText = "النتيجة: " + data.result;
    })
    .catch(error => {
        statusText.innerText = "حدث خطأ!";
        console.error("Error:", error);
    });
}
