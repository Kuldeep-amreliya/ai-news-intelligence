export function ErrorState() {
  return (
    <div style={{ padding: "60px 0", textAlign: "center" }}>
      <p style={{ color: "#f87171", fontSize: 14, marginBottom: 8 }}>
        Could not reach the server.
      </p>
      <p style={{ color: "#444", fontSize: 12 }}>
        Make sure the FastAPI server is running on port 8000.
      </p>
    </div>
  );
}
