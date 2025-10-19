import React from 'react';

// Eranos Staff Dashboard - Single-file React component using TailwindCSS
// Default export a single component suitable for preview in canvas.

const KPI = ({title, value, change, caption}) => (
  <div className="p-4 bg-white rounded-2xl shadow-sm border">
    <div className="text-sm font-medium text-gray-500">{title}</div>
    <div className="mt-2 flex items-baseline space-x-3">
      <div className="text-2xl font-semibold">{value}</div>
      <div className={`text-sm font-medium ${change.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>{change}</div>
    </div>
    <div className="text-xs text-gray-400 mt-1">{caption}</div>
  </div>
);

const TaskItem = ({task}) => (
  <div className="flex items-start space-x-3 p-3 bg-white rounded-lg border">
    <input type="checkbox" className="mt-1" checked={task.done} readOnly />
    <div className="flex-1">
      <div className="flex justify-between">
        <div className="font-medium">{task.title}</div>
        <div className="text-xs text-gray-400">{task.due}</div>
      </div>
      <div className="text-xs text-gray-500 mt-1">Assigned to: {task.assignee}</div>
    </div>
  </div>
);

const ClientRow = ({c}) => (
  <tr className="bg-white">
    <td className="px-4 py-3">{c.name}</td>
    <td className="px-4 py-3">{c.service}</td>
    <td className="px-4 py-3">{c.status}</td>
    <td className="px-4 py-3">{c.nextAction}</td>
    <td className="px-4 py-3">{c.balance}</td>
  </tr>
);

export default function EranosStaffDashboard(){
  const kpis = [
    {title: 'Active Clients', value: '128', change: '+4', caption: 'Compared to last month'},
    {title: 'Open Tasks', value: '42', change: '-6', caption: 'Due within 7 days'},
    {title: 'Invoices Outstanding', value: 'GHS 45,200', change: '+12%', caption: 'Total unpaid'},
    {title: 'Avg Turnaround', value: '3.2 days', change: '-0.4', caption: 'Onboarding → Active'}
  ];

  const tasks = [
    {title: 'Verify KYC — Acme Trading', due: '2025-10-21', assignee: 'Ama Osei', done: false},
    {title: 'Prepare Q3 VAT Filing — MiningCo', due: '2025-10-25', assignee: 'Kwesi Adu', done: false},
    {title: 'Audit draft review — Solar Ltd', due: '2025-11-02', assignee: 'Sika Mensah', done: false}
  ];

  const clients = [
    {name: 'Acme Trading', service: 'Tax Advisory', status: 'Pre-Active', nextAction: 'Verify Payment', balance: 'GHS 5,150'},
    {name: 'MiningCo', service: 'Audit & Assurance', status: 'Active', nextAction: 'Schedule Fieldwork', balance: 'GHS 0'},
    {name: 'Solar Ltd', service: 'Payroll', status: 'Active', nextAction: 'Upload Payslips', balance: 'GHS 1,200'}
  ];

  return (
    <div className="min-h-screen bg-gray-50 text-gray-800 p-6">
      <header className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center text-white font-bold">E</div>
          <div>
            <div className="text-lg font-bold">Eranos Staff Dashboard</div>
            <div className="text-sm text-gray-500">Manage clients, tasks, documents & compliance (powered by WP Client Portal)</div>
          </div>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-sm text-gray-600">Signed in as <strong>ama@eranos.com</strong></div>
          <button className="px-4 py-2 bg-white rounded-xl border">Profile</button>
        </div>
      </header>

      <div className="grid grid-cols-12 gap-6">
        {/* Left navigation */}
        <aside className="col-span-2 bg-white rounded-2xl p-4 h-[72vh] border">
          <nav className="space-y-2 text-sm">
            <div className="font-semibold mb-2">Navigation</div>
            <a className="block p-2 rounded-lg hover:bg-gray-50">Overview</a>
            <a className="block p-2 rounded-lg hover:bg-gray-50">Clients</a>
            <a className="block p-2 rounded-lg hover:bg-gray-50">Tasks</a>
            <a className="block p-2 rounded-lg hover:bg-gray-50">Documents</a>
            <a className="block p-2 rounded-lg hover:bg-gray-50">Invoices</a>
            <a className="block p-2 rounded-lg hover:bg-gray-50">Calendar</a>
            <a className="block p-2 rounded-lg hover:bg-gray-50">Reports</a>
            <a className="block p-2 rounded-lg hover:bg-gray-50">Settings</a>
          </nav>

          <div className="mt-6 text-xs text-gray-400">Retention policy: 6 years (tax records). Compliance reminders enabled.</div>
        </aside>

        {/* Main content */}
        <main className="col-span-7">
          <section className="grid grid-cols-4 gap-4 mb-6">
            {kpis.map(k=> <KPI key={k.title} {...k} />)}
          </section>

          <section className="mb-6">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-semibold">Pending Tasks</h3>
              <div className="text-sm text-gray-500">Sort: Due soon</div>
            </div>
            <div className="space-y-3">
              {tasks.map(t=> <TaskItem key={t.title} task={t} />)}
            </div>
          </section>

          <section className="bg-white rounded-2xl p-4 border">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold">Client Quick List</h3>
              <div className="text-sm text-gray-500">Search / Filter</div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full min-w-[700px] text-left">
                <thead className="text-xs text-gray-500">
                  <tr>
                    <th className="px-4 py-2">Client</th>
                    <th className="px-4 py-2">Service</th>
                    <th className="px-4 py-2">Status</th>
                    <th className="px-4 py-2">Next Action</th>
                    <th className="px-4 py-2">Balance</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {clients.map(c=> <ClientRow key={c.name} c={c} />)}
                </tbody>
              </table>
            </div>
          </section>
        </main>

        {/* Right sidebar */}
        <aside className="col-span-3 space-y-4">
          <div className="bg-white p-4 rounded-2xl border">
            <div className="flex items-center justify-between mb-3">
              <div>
                <div className="text-sm font-medium">Notifications</div>
                <div className="text-xs text-gray-400">Important portal events</div>
              </div>
              <div className="text-xs text-indigo-600 font-medium">See all</div>
            </div>
            <ul className="space-y-2 text-sm text-gray-700">
              <li className="border p-2 rounded">Acme Trading uploaded receipt (awaiting verification)</li>
              <li className="border p-2 rounded">New client registration — pending phone verification</li>
              <li className="border p-2 rounded">VAT filing deadline: 2025-10-28</li>
            </ul>
          </div>

          <div className="bg-white p-4 rounded-2xl border">
            <div className="flex items-center justify-between mb-3">
              <div>
                <div className="text-sm font-medium">Documents (Quick Actions)</div>
                <div className="text-xs text-gray-400">Upload / Verify / Share</div>
              </div>
              <button className="px-3 py-1 border rounded">Upload</button>
            </div>
            <div className="text-xs text-gray-500">Recent Uploads</div>
            <ul className="mt-2 text-sm space-y-2">
              <li className="flex justify-between"><span>RGD — Acme Trading.pdf</span><span className="text-gray-400">Uploaded 2h</span></li>
              <li className="flex justify-between"><span>Receipt — Acme.jpg</span><span className="text-gray-400">Uploaded 3h</span></li>
            </ul>
          </div>

          <div className="bg-white p-4 rounded-2xl border">
            <div className="text-sm font-medium mb-2">Upcoming Calendar</div>
            <div className="text-xs text-gray-500 mb-3">Key deadlines & meetings</div>
            <ul className="space-y-2 text-sm">
              <li>2025-10-21 — KYC verification (Acme Trading)</li>
              <li>2025-10-25 — VAT submission (MiningCo)</li>
              <li>2025-11-02 — Audit fieldwork (Solar Ltd)</li>
            </ul>
          </div>
        </aside>
      </div>

      <footer className="mt-6 text-xs text-gray-400">Eranos Consulting — Contact: +233559331276 / +233548000740 • apexsourceventures@gmail.com</footer>
    </div>
  );
}
