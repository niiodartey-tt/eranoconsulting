import React from 'react';

// Eranos Client Dashboard - Single-file React component using TailwindCSS
// Purpose: front-end client portal view with Documents, Tasks, Invoices, Messages

const KPI = ({title, value, hint}) => (
  <div className="p-4 bg-white rounded-2xl shadow-sm border">
    <div className="text-sm font-medium text-gray-500">{title}</div>
    <div className="mt-2 text-2xl font-semibold">{value}</div>
    {hint && <div className="text-xs text-gray-400 mt-1">{hint}</div>}
  </div>
);

const Task = ({t}) => (
  <div className="flex items-start justify-between p-3 bg-white rounded-lg border">
    <div>
      <div className="font-medium">{t.title}</div>
      <div className="text-xs text-gray-500">Due: {t.due} • Assigned: {t.assignee}</div>
    </div>
    <div className="flex items-center gap-2">
      <button className="px-3 py-1 border rounded text-sm">Upload</button>
      <button className={`px-3 py-1 rounded text-sm ${t.status==='Overdue' ? 'bg-red-600 text-white' : 'bg-green-600 text-white'}`}>{t.status}</button>
    </div>
  </div>
);

export default function EranosClientDashboard(){
  const kpis = [
    {title: 'Open Tasks', value: 3, hint: 'Tasks requiring your input'},
    {title: 'Outstanding Balance', value: 'GHS 5,150', hint: 'Due within 14 days'},
    {title: 'Signed Engagement', value: 'Pending', hint: 'Sign to activate services'},
    {title: 'Messages', value: 2, hint: 'Unread messages from your consultant'}
  ];

  const tasks = [
    {title: 'Complete Payroll Template', due: '2025-11-05', assignee: 'You', status: 'Pending'},
    {title: 'Upload FY2024 Bank Statement', due: '2025-10-28', assignee: 'You', status: 'Overdue'},
    {title: 'Provide Director IDs', due: '2025-11-12', assignee: 'You', status: 'Pending'}
  ];

  const invoices = [
    {no: 'INV-2025-001', date: '2025-10-01', due: '2025-10-15', amount: 'GHS 5,150', status: 'Unpaid'},
    {no: 'INV-2025-002', date: '2025-08-01', due: '2025-08-15', amount: 'GHS 12,000', status: 'Paid'}
  ];

  const documents = [
    {name: 'Certificate of Incorporation.pdf', uploaded: '2025-10-16'},
    {name: 'Proof of Address.jpg', uploaded: '2025-10-16'},
    {name: 'Payment-Receipt-INV-2025-001.jpg', uploaded: '2025-10-17'}
  ];

  const messages = [
    {from: 'Ama Osei (Account Manager)', preview: 'Please sign the engagement letter to activate your account.', time: '2d'},
    {from: 'Accounts', preview: 'We received your payment but need bank reference clarification.', time: '5d'}
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-6 text-gray-800">
      <header className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center text-white font-bold">E</div>
          <div>
            <div className="text-lg font-bold">Client Portal — Eranos Consulting</div>
            <div className="text-sm text-gray-500">Welcome back — Acme Trading</div>
          </div>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-sm text-gray-600">Signed in as <strong>admin@acmetrade.com</strong></div>
          <button className="px-4 py-2 bg-white rounded-xl border">Profile</button>
        </div>
      </header>

      <div className="grid grid-cols-12 gap-6">
        <aside className="col-span-2 bg-white rounded-2xl p-4 h-[72vh] border">
          <nav className="space-y-2 text-sm">
            <div className="font-semibold mb-2">Quick Links</div>
            <a className="block p-2 rounded-lg hover:bg-gray-50">Overview</a>
            <a className="block p-2 rounded-lg hover:bg-gray-50">Documents</a>
            <a className="block p-2 rounded-lg hover:bg-gray-50">Invoices</a>
            <a className="block p-2 rounded-lg hover:bg-gray-50">Tasks</a>
            <a className="block p-2 rounded-lg hover:bg-gray-50">Messages</a>
            <a className="block p-2 rounded-lg hover:bg-gray-50">Calendar</a>
            <a className="block p-2 rounded-lg hover:bg-gray-50">Support</a>
            <a className="block p-2 rounded-lg hover:bg-gray-50">Settings</a>
          </nav>

          <div className="mt-6 text-xs text-gray-400">Retention policy: documents retained for 6 years. See privacy settings.</div>
        </aside>

        <main className="col-span-7">
          <section className="grid grid-cols-4 gap-4 mb-6">
            {kpis.map(k => <KPI key={k.title} {...k} />)}
          </section>

          <section className="mb-6">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-semibold">Pending Tasks</h3>
              <div className="text-sm text-gray-500">Action required</div>
            </div>
            <div className="space-y-3">
              {tasks.map(t => <Task key={t.title} t={t} />)}
            </div>
          </section>

          <section className="bg-white p-4 rounded-2xl border">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold">Invoices & Payments</h3>
              <div className="text-sm text-gray-500">Upload receipt after payment</div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left min-w-[700px]">
                <thead className="text-xs text-gray-500">
                  <tr>
                    <th className="px-4 py-2">Invoice</th>
                    <th className="px-4 py-2">Issued</th>
                    <th className="px-4 py-2">Due</th>
                    <th className="px-4 py-2">Amount</th>
                    <th className="px-4 py-2">Status</th>
                    <th className="px-4 py-2">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {invoices.map(inv => (
                    <tr key={inv.no} className="bg-white">
                      <td className="px-4 py-3">{inv.no}</td>
                      <td className="px-4 py-3">{inv.date}</td>
                      <td className="px-4 py-3">{inv.due}</td>
                      <td className="px-4 py-3">{inv.amount}</td>
                      <td className="px-4 py-3">{inv.status}</td>
                      <td className="px-4 py-3"><button className="px-3 py-1 border rounded text-sm">Upload Receipt</button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </main>

        <aside className="col-span-3 space-y-4">
          <div className="bg-white p-4 rounded-2xl border">
            <div className="flex items-center justify-between mb-3">
              <div>
                <div className="text-sm font-medium">Messages</div>
                <div className="text-xs text-gray-400">Secure chat with your consultant</div>
              </div>
              <button className="px-3 py-1 border rounded text-sm">New Message</button>
            </div>
            <ul className="space-y-2 text-sm">
              {messages.map((m,i) => (
                <li key={i} className="border p-2 rounded">
                  <div className="font-medium">{m.from}</div>
                  <div className="text-xs text-gray-500">{m.preview} • {m.time}</div>
                </li>
              ))}
            </ul>
          </div>

          <div className="bg-white p-4 rounded-2xl border">
            <div className="flex items-center justify-between mb-3">
              <div>
                <div className="text-sm font-medium">Your Documents</div>
                <div className="text-xs text-gray-400">Recent uploads & KYC</div>
              </div>
              <button className="px-3 py-1 border rounded text-sm">Upload</button>
            </div>
            <ul className="mt-2 text-sm space-y-2">
              {documents.map((d,i) => (
                <li key={i} className="flex justify-between"><span>{d.name}</span><span className="text-gray-400">{d.uploaded}</span></li>
              ))}
            </ul>
            <div className="mt-3 text-xs text-gray-500">Accepted formats: PDF, JPG, PNG. See onboarding for required KYC docs.</div>
          </div>

          <div className="bg-white p-4 rounded-2xl border">
            <div className="text-sm font-medium mb-2">Engagement Letter</div>
            <div className="text-xs text-gray-400 mb-3">Review and sign to activate services</div>
            <div className="p-3 border rounded">
              <div className="font-medium">Engagement-ACME-2025.pdf</div>
              <div className="text-xs text-gray-500">Status: Awaiting signature</div>
              <div className="mt-3 flex gap-2"><button className="px-3 py-1 bg-indigo-600 text-white rounded text-sm">Review</button><button className="px-3 py-1 border rounded text-sm">Sign</button></div>
            </div>
          </div>

          <div className="bg-white p-4 rounded-2xl border">
            <div className="text-sm font-medium mb-2">Support & Resources</div>
            <div className="text-xs text-gray-400 mb-3">How-to guides & contact</div>
            <ul className="space-y-2 text-sm">
              <li>How to upload receipts</li>
              <li>VAT filing checklist</li>
              <li>Contact: support@eranoconsulting.com</li>
            </ul>
          </div>
        </aside>
      </div>

      <footer className="mt-6 text-xs text-gray-400">Eranos Consulting — Contact: +233559331276 • privacy@eranoconsulting.com</footer>
    </div>
  );
}
