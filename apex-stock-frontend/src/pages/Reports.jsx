import { reportAPI } from '../services/api';
import { FileText, Download, AlertTriangle, Package, TruckIcon } from 'lucide-react';
import './Reports.css';

export default function Reports() {
  const reports = [
    {
      title: 'Inventory Report (PDF)',
      description: 'Complete inventory list with all details',
      icon: Package,
      color: 'blue',
      action: () => reportAPI.downloadInventoryPDF(),
    },
    {
      title: 'Inventory Report (CSV)',
      description: 'Inventory data in spreadsheet format',
      icon: FileText,
      color: 'green',
      action: () => reportAPI.downloadInventoryCSV(),
    },
    {
      title: 'Low Stock Alert (PDF)',
      description: 'Items that need immediate reordering',
      icon: AlertTriangle,
      color: 'red',
      action: () => reportAPI.downloadLowStockPDF(),
    },
    {
      title: 'Suppliers Report (CSV)',
      description: 'Complete supplier contact list',
      icon: TruckIcon,
      color: 'purple',
      action: () => reportAPI.downloadSuppliersCSV(),
    },
  ];

  return (
    <div className="page-container">
      <h1 className="page-title">Reports & Downloads</h1>
      <p className="page-subtitle">
        Generate and download various reports for your inventory system
      </p>

      <div className="reports-grid">
        {reports.map((report, index) => (
          <div key={index} className="report-card">
            <div className={`report-icon report-icon-${report.color}`}>
              <report.icon size={32} />
            </div>
            <h3 className="report-title">{report.title}</h3>
            <p className="report-description">{report.description}</p>
            <button onClick={report.action} className="download-button">
              <Download size={18} />
              <span>Download</span>
            </button>
          </div>
        ))}
      </div>

      <div className="info-box">
        <FileText size={24} />
        <div>
          <h4>About Reports</h4>
          <p>
            All reports are generated in real-time based on your current inventory data.
            PDF reports include formatting and styling, while CSV files can be opened in
            Excel or Google Sheets for further analysis.
          </p>
        </div>
      </div>
    </div>
  );
}