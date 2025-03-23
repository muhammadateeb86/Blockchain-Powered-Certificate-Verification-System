document.getElementById("uploadForm").addEventListener("submit", async function (event) {
    event.preventDefault(); // Prevent form from refreshing the page

    const fileInput = document.getElementById("fileInput");
    const studentId = document.getElementById("studentId").value.trim();
    const responseDiv = document.getElementById("response");
    const qrCodeDiv = document.getElementById("qrcode");

    responseDiv.innerHTML = "";
    qrCodeDiv.innerHTML = "";

    if (!fileInput.files.length) {
        responseDiv.innerHTML = `<p style="color:red;">Please select a certificate file.</p>`;
        return;
    }
    if (!studentId) {
        responseDiv.innerHTML = `<p style="color:red;">Please enter a Student ID.</p>`;
        return;
    }

    const formData = new FormData();
    formData.append("certificate", fileInput.files[0]);
    formData.append("student_id", studentId);

    try {
        console.log("Sending request with student_id:", studentId);
        const response = await fetch("http://127.0.0.1:5000/upload-degree-certificate", {
            method: "POST",
            body: formData
        });

        console.log("Response status:", response.status);
        console.log("Response headers:", [...response.headers.entries()]);

        const result = await response.json();
        console.log("Response data:", result);

        if (response.ok) {
            responseDiv.innerHTML = `
                <h3>Certificate Uploaded Successfully!</h3>
                <p><strong>Certificate Hash:</strong> ${result.certificate_hash}</p>
                <p><strong>IPFS Hash:</strong> ${result.ipfs_hash}</p>
                <p><strong>Blockchain TX ID:</strong> ${result.blockchain_tx_id}</p>
            `;

            const studentInfo = await fetchStudentInfo(studentId);
            const qrData = JSON.stringify({
                student_id: studentId,
                student_name: studentInfo.name || "Unknown",
                certificate_hash: result.certificate_hash
            });

            new QRCode(qrCodeDiv, {
                text: qrData,
                width: 128,
                height: 128
            });
        } else {
            responseDiv.innerHTML = `<p style="color:red;">Error: ${result.error}</p>`;
        }
    } catch (error) {
        console.error("Upload error:", error);
        responseDiv.innerHTML = `<p style="color:red;">Upload failed: ${error.message}</p>`;
    }
});

async function fetchStudentInfo(studentId) {
    return { name: "John Doe" }; // Mock data
}