import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

const API = "http://localhost:8002";

function App() {
  const [deployments, setDeployments] = useState([]);
  const [selectedDep, setSelectedDep] = useState(null);
  const [pods, setPods] = useState([]);
  const [formData, setFormData] = useState({
    name: "",
    image: "nginx:latest",
    replicas: 1,
    port: 8080,
    cpu_request: "100m",
    memory_request: "128Mi",
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchDeployments();
  }, []);

  const fetchDeployments = async () => {
    try {
      const res = await axios.get(`${API}/deployments`);
      setDeployments(res.data.deployments || []);
    } catch (err) {
      console.error("Failed to fetch deployments:", err);
    }
  };

  const fetchPods = async (deploymentId) => {
    try {
      const res = await axios.get(`${API}/deployments/${deploymentId}/pods`);
      setPods(res.data.pods || []);
    } catch (err) {
      console.error("Failed to fetch pods:", err);
    }
  };

  const handleSelectDeployment = (dep) => {
    setSelectedDep(dep);
    fetchPods(dep.id);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === "replicas" || name === "port" ? parseInt(value) : value,
    }));
  };

  const handleDeploy = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await axios.post(`${API}/deployments`, formData);
      alert(`Deployment created: ${res.data.name}`);
      setFormData({
        name: "",
        image: "nginx:latest",
        replicas: 1,
        port: 8080,
        cpu_request: "100m",
        memory_request: "128Mi",
      });
      fetchDeployments();
    } catch (err) {
      alert("Failed to create deployment: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (depId) => {
    if (!window.confirm("Delete this deployment?")) return;
    try {
      await axios.delete(`${API}/deployments/${depId}`);
      alert("Deployment deleted");
      setSelectedDep(null);
      setPods([]);
      fetchDeployments();
    } catch (err) {
      alert("Failed to delete: " + err.message);
    }
  };

  return (
    <div className="container">
      <h1>K8s Deployment Platform</h1>

      <div className="two-column">
        <section className="panel">
          <h2>Deploy Application</h2>
          <form onSubmit={handleDeploy}>
            <div className="form-group">
              <label>Application Name</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                placeholder="my-app"
                required
              />
            </div>

            <div className="form-group">
              <label>Docker Image</label>
              <input
                type="text"
                name="image"
                value={formData.image}
                onChange={handleInputChange}
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Replicas</label>
                <input
                  type="number"
                  name="replicas"
                  min="1"
                  max="10"
                  value={formData.replicas}
                  onChange={handleInputChange}
                />
              </div>
              <div className="form-group">
                <label>Port</label>
                <input
                  type="number"
                  name="port"
                  value={formData.port}
                  onChange={handleInputChange}
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>CPU Request</label>
                <input
                  type="text"
                  name="cpu_request"
                  value={formData.cpu_request}
                  onChange={handleInputChange}
                  placeholder="100m"
                />
              </div>
              <div className="form-group">
                <label>Memory Request</label>
                <input
                  type="text"
                  name="memory_request"
                  value={formData.memory_request}
                  onChange={handleInputChange}
                  placeholder="128Mi"
                />
              </div>
            </div>

            <button type="submit" disabled={loading} className="btn-primary">
              {loading ? "Deploying..." : "Deploy"}
            </button>
          </form>
        </section>

        <section className="panel">
          <h2>Deployments ({deployments.length})</h2>
          <div className="deployments-list">
            {deployments.length === 0 ? (
              <p className="empty">No deployments</p>
            ) : (
              deployments.map((dep) => (
                <div
                  key={dep.id}
                  className={`deployment-item ${selectedDep?.id === dep.id ? "selected" : ""}`}
                  onClick={() => handleSelectDeployment(dep)}
                >
                  <div className="dep-header">
                    <strong>{dep.name}</strong>
                    <span className="badge">{dep.status}</span>
                  </div>
                  <p className="dep-info">Image: {dep.image}</p>
                  <p className="dep-info">
                    Replicas: {dep.pod_count}/{dep.replicas}
                  </p>
                  <p className="dep-time">
                    Created: {new Date(dep.created_at).toLocaleString()}
                  </p>
                </div>
              ))
            )}
          </div>
        </section>
      </div>

      {selectedDep && (
        <section className="panel">
          <div className="section-header">
            <h2>Pods - {selectedDep.name}</h2>
            <button
              onClick={() => handleDelete(selectedDep.id)}
              className="btn-danger"
            >
              Delete Deployment
            </button>
          </div>

          <div className="pods-grid">
            {pods.length === 0 ? (
              <p className="empty">No pods</p>
            ) : (
              pods.map((pod) => (
                <div key={pod.name} className="pod-card">
                  <p>
                    <strong>{pod.name}</strong>
                  </p>
                  <p>
                    Status: <span className="status-badge">{pod.status}</span>
                  </p>
                  <p>CPU: {pod.cpu_usage}</p>
                  <p>Memory: {pod.memory_usage}</p>
                  <p>Restarts: {pod.restarts}</p>
                </div>
              ))
            )}
          </div>
        </section>
      )}
    </div>
  );
}

export default App;
