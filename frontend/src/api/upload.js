const BASE_URL = "http://localhost:8000"; // Change if needed

export async function uploadDocument(file) {
  const formData = new FormData();

  formData.append("application_id", "APP001");
  formData.append("file", file);

  const response = await fetch(`${BASE_URL}/api/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Upload failed");
  }

  return await response.json();
}