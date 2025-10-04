import { useState, useEffect } from 'react';
import { supplierAPI } from '../services/api';
import { Plus, Edit, Trash2, TruckIcon } from 'lucide-react';
import './Suppliers.css';

export default function Suppliers() {
  const [suppliers, setSuppliers] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [editingSupplier, setEditingSupplier] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    contact_person: '',
    email: '',
    phone: '',
    address: '',
  });

  useEffect(() => {
    fetchSuppliers();
  }, []);

  const fetchSuppliers = async () => {
    try {
      const response = await supplierAPI.getAll();
      setSuppliers(response.data);
    } catch (error) {
      console.error('Error fetching suppliers:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingSupplier) {
        await supplierAPI.update(editingSupplier.id, formData);
      } else {
        await supplierAPI.create(formData);
      }
      fetchSuppliers();
      closeModal();
    } catch (error) {
      alert(error.response?.data?.error || 'Operation failed');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this supplier?')) return;
    try {
      await supplierAPI.delete(id);
      fetchSuppliers();
    } catch (error) {
      alert(error.response?.data?.error || 'Delete failed');
    }
  };

  const openModal = (supplier = null) => {
    if (supplier) {
      setEditingSupplier(supplier);
      setFormData({
        name: supplier.name,
        contact_person: supplier.contact_person || '',
        email: supplier.email || '',
        phone: supplier.phone || '',
        address: supplier.address || '',
      });
    } else {
      setEditingSupplier(null);
      setFormData({
        name: '',
        contact_person: '',
        email: '',
        phone: '',
        address: '',
      });
    }
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingSupplier(null);
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Supplier Management</h1>
        <button onClick={() => openModal()} className="btn-primary">
          <Plus size={20} />
          <span>Add Supplier</span>
        </button>
      </div>

      {/* Suppliers Grid */}
      <div className="suppliers-grid">
        {suppliers.map((supplier) => (
          <div key={supplier.id} className="supplier-card">
            <div className="supplier-header">
              <div className="supplier-icon">
                <TruckIcon size={24} />
              </div>
              <div className="supplier-actions">
                <button
                  onClick={() => openModal(supplier)}
                  className="btn-icon btn-edit"
                  title="Edit"
                >
                  <Edit size={18} />
                </button>
                <button
                  onClick={() => handleDelete(supplier.id)}
                  className="btn-icon btn-delete"
                  title="Delete"
                >
                  <Trash2 size={18} />
                </button>
              </div>
            </div>
            <h3 className="supplier-name">{supplier.name}</h3>
            <div className="supplier-details">
              {supplier.contact_person && (
                <p><strong>Contact:</strong> {supplier.contact_person}</p>
              )}
              {supplier.email && (
                <p><strong>Email:</strong> {supplier.email}</p>
              )}
              {supplier.phone && (
                <p><strong>Phone:</strong> {supplier.phone}</p>
              )}
              {supplier.address && (
                <p><strong>Address:</strong> {supplier.address}</p>
              )}
              <p className="items-count">
                <strong>Items Supplied:</strong> {supplier.items_count}
              </p>
            </div>
          </div>
        ))}
      </div>

      {suppliers.length === 0 && (
        <div className="empty-state">
          <TruckIcon size={48} />
          <p>No suppliers yet. Add your first supplier to get started!</p>
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2 className="modal-title">
              {editingSupplier ? 'Edit Supplier' : 'Add New Supplier'}
            </h2>
            <form onSubmit={handleSubmit} className="modal-form">
              <input
                type="text"
                placeholder="Supplier Name *"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
              <input
                type="text"
                placeholder="Contact Person"
                value={formData.contact_person}
                onChange={(e) => setFormData({ ...formData, contact_person: e.target.value })}
              />
              <input
                type="email"
                placeholder="Email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              />
              <input
                type="tel"
                placeholder="Phone"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              />
              <textarea
                placeholder="Address"
                value={formData.address}
                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                rows="3"
              />
              <div className="modal-buttons">
                <button type="submit" className="btn-primary">
                  {editingSupplier ? 'Update' : 'Create'}
                </button>
                <button type="button" onClick={closeModal} className="btn-secondary">
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}