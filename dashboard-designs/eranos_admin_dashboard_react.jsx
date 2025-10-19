import React from 'react';

// Eranos Admin Dashboard - Single-file React component using TailwindCSS
// Default export a single component suitable for preview in canvas.

const Stat = ({title, value, note}) => (
  <div className="p-4 bg-white rounded-2xl shadow-sm border">
    <div className="text-sm font-medium text-gray-500">{title}</div>
    <div className="mt-2 flex items-baseline justify-between">
      <div className="text-2xl font-semibold">{value}</div>
      <div className="text-xs text-gray-400">{note}</div>
    </div>
  </div>
);

const ActionButton = ({children}) => (
  <button className="px-3 py-1 bg-indigo-600 text-white rounded-xl text-sm">{children}</button>
);

export default function EranosAdminDashboard(){
  const stats = [
    {title: 'Total Clients', value: 182, note: 'All statuses'},
    {title: 'Pending Verifications', value: 7, note: 'KYC or payment'},
    {title: 'Outstanding Invoices', value: 'GHS 72,450', note: 'Aging >30 days: GHS 18,200'},
    {title: 'Active Staff', value: 14, note: 'Role-based access'}
  ];

  const verifications = [
    {client: 'Acme Trading', type: 'Payment Receipt', received: '2025-10-17', reviewer: 'Ama', status: 'Awaiting Bank Match'},
    {client: 'MiningCo', type: 'KYC Docs', received: '2025-10-16', reviewer: 'Kwesi', status: 'Documents OK'},
    {client: 'Solar Ltd', type: 'Engagement Sign', received: '2025-10-15', reviewer: 'Sika', status: 'Pending Signature'}
  ];

  const recentLog = [
    {time: '2025-10-18 09:12', user: 'admin@eranos.com', action: 'Created client: GreenFoods'},
    {time: '2025-10-18 08:45', user: 'ama@eranos.com', action: 'Verified payment: Acme Trading'},
    {time: '2025-10-17 17:02', user: 'kwesi@eranos.com', action: 'Uploaded engagement: MiningCo'}
  ];

  const staff = [
    {name: 'Ama Osei', role: 'Senior Accountant', email: 'ama@eranos.com', status: 'Active'},
    {name: 'Kwesi Adu', role: 'Junior Accountant', email: 'kwesi@eranos.com', status: 'Active'},
    {name: 'Sika Mensah', role: 'Admin', email: 'sika@eranos.com', status: 'Active'}
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-6 text-gray-800">
      <header className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 bg-gradient-to-br from-green-600 to-teal-600 rounded-lg flex items-center justify-center text-white font-bold">E</div>
          <div>
            <div className="text-lg font-bold">Eranos Admin Dashboard</div>
            <div className="text-sm text-gray-500">Administration, compliance & system controls.</div>
          </div>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-sm text-gray-600">Signed in as <strong>admin@eranos.com</strong></div>
          <ActionButton>New Client</ActionButton>
        </div>
      </header>

      <div className="grid grid-cols-12 gap-6">
        <aside className="col-span-2 bg-white rounded-2xl p-4 h-[72vh] border">
          <nav className="space-y-2 text-sm">
            <div className="font-semibold mb-2">Admin Menu</div>
            <a className="block p-2 rounded-lg hover:bg-gray-50">Overview</a>
            <a className="block p-2 rounded-lg hover:bg-gray-50">Client Approvals</a>
            <a className="block p-2 rounded-lg hover:bg-gray-50">Staff & Roles</a>
            <a className="block p-2 rounded-lg hover:bg-gray-50">Documents</a>
            <a className="block p-2 rounded-lg hover:bg-gray-50">Billing & Payments</a>
            <a className="block p-2 rounded-lg hover:bg-gray-50">Audit Logs</a>
            <a className="block p-2 rounded-lg hover:bg-gray-50">Reports</a>
            <a className="block p-2 rounded-lg hover:bg-gray-50">Integrations</a>
            <a className="block p-2 rounded-lg hover:bg-gray-50">Settings</a>
          </nav>
          <div className="mt-6 text-xs text-gray-400">Retention policy: 6 years (tax records). Compliance reminders enabled.</div>
        </aside>

        <main className="col-span-7">
          <section className="grid grid-cols-4 gap-4 mb-6">
            {stats.map(s => <Stat key={s.title} {...s} />)}
          </section>

          <section className="mb-6 bg-white p-4 rounded-2xl border">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h3 className="text-lg font-semibold">Client Approvals & Verifications</h3>
                <div className="text-xs text-gray-400">Quickly approve pre-active accounts, verify KYC and payments.</div>
              </div>
              <div className="flex items-center space-x-2">
                <ActionButton>Batch Approve</ActionButton>
                <button className="px-3 py-1 border rounded text-sm">Export CSV</button>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left min-w-[700px]">
                <thead className="text-xs text-gray-500">
                  <tr>
                    <th className="px-4 py-2">Client</th>
                    <th className="px-4 py-2">Type</th>
                    <th className="px-4 py-2">Received</th>
                    <th className="px-4 py-2">Reviewer</th>
                    <th className="px-4 py-2">Status</th>
                    <th className="px-4 py-2">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {verifications.map(v => (
                    <tr key={v.client} className="bg-white">
                      <td className="px-4 py-3">{v.client}</td>
                      <td className="px-4 py-3">{v.type}</td>
                      <td className="px-4 py-3">{v.received}</td>
                      <td className="px-4 py-3">{v.reviewer}</td>
                      <td className="px-4 py-3">{v.status}</td>
                      <td className="px-4 py-3">
                        <div className="flex gap-2">
                          <button className="px-2 py-1 border rounded text-sm">View</button>
                          <button className="px-2 py-1 bg-green-600 text-white rounded text-sm">Approve</button>
                          <button className="px-2 py-1 bg-red-600 text-white rounded text-sm">Reject</button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section className="bg-white p-4 rounded-2xl border">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-semibold">Financial Snapshot</h3>
              <div className="text-xs text-gray-400">Invoices, payments and aging summary</div>
            </div>
            <div className="grid grid-cols-3 gap-4 mb-3">
              <div className="p-3 border rounded">Total Invoices: <strong>512</strong></div>
              <div className="p-3 border rounded">Paid: <strong>GHS 320,450</strong></div>
              <div className="p-3 border rounded">Overdue: <strong>GHS 18,200</strong></div>
            </div>
            <div className="text-sm text-gray-500">Generate a detailed aging report or export to accounting software (QuickBooks / Sage).</div>
          </section>
        </main>

        <aside className="col-span-3 space-y-4">
          <div className="bg-white p-4 rounded-2xl border">
            <div className="flex items-center justify-between mb-3">
              <div>
                <div className="text-sm font-medium">System Audit Log</div>
                <div className="text-xs text-gray-400">Recent critical actions</div>
              </div>
              <button className="px-3 py-1 border rounded text-sm">View All</button>
            </div>
            <ul className="text-sm space-y-2">
              {recentLog.map(l => (
                <li key={l.time} className="border p-2 rounded">{l.time} — <strong>{l.user}</strong> — {l.action}</li>
              ))}
            </ul>
          </div>

          <div className="bg-white p-4 rounded-2xl border">
            <div className="flex items-center justify-between mb-3">
              <div>
                <div className="text-sm font-medium">Staff & Roles</div>
                <div className="text-xs text-gray-400">Manage user access and permissions</div>
              </div>
              <ActionButton>Invite Staff</ActionButton>
            </div>
            <ul className="text-sm space-y-2">
              {staff.map(s => (
                <li key={s.email} className="flex justify-between items-center border p-2 rounded">
                  <div>
                    <div className="font-medium">{s.name}</div>
                    <div className="text-xs text-gray-400">{s.role} • {s.email}</div>
                  </div>
                  <div className="text-sm text-gray-500">{s.status}</div>
                </li>
              ))}
            </ul>
          </div>

          <div className="bg-white p-4 rounded-2xl border">
            <div className="text-sm font-medium mb-2">Integrations</div>
            <div className="text-xs text-gray-400 mb-3">Connected systems</div>
            <ul className="space-y-2 text-sm">
              <li className="flex justify-between"><span>WP Client Portal</span><span className="text-gray-400">Connected</span></li>
              <li className="flex justify-between"><span>QuickBooks</span><span className="text-gray-400">Not Connected</span></li>
              <li className="flex justify-between"><span>Bank Feed</span><span className="text-gray-400">Pending</span></li>
            </ul>
            <div className="mt-3 text-xs text-gray-500">Use integrations to automate payment verification and accounting exports. See proposal integrations (WP Client Portal, Uncanny Automator). </div>
          </div>
        </aside>
      </div>

      <footer className="mt-6 text-xs text-gray-400">Eranos Consulting — Admin • Data retention: 6 years • privacy@eranoconsulting.com</footer>
    </div>
  );
}
