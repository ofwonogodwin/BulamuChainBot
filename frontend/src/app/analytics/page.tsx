'use client';

import React, { useState, useEffect } from 'react';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell,
    LineChart,
    Line
} from 'recharts';
import {
    Users,
    Activity,
    AlertTriangle,
    TrendingUp,
    Calendar,
    MapPin,
    Clock,
    Heart,
    ArrowLeft,
    Download,
    Filter
} from 'lucide-react';
import Link from 'next/link';

interface DashboardStats {
    totalConsultations: number;
    emergencyAlerts: number;
    activeUsers: number;
    avgResponseTime: string;
}

interface SymptomData {
    symptom: string;
    count: number;
    percentage: number;
    [key: string]: any;
}

interface TimeSeriesData {
    date: string;
    consultations: number;
    emergencies: number;
    [key: string]: any;
}

export default function AnalyticsDashboard() {
    const [stats, setStats] = useState<DashboardStats>({
        totalConsultations: 0,
        emergencyAlerts: 0,
        activeUsers: 0,
        avgResponseTime: '0s'
    });

    const [symptomData, setSymptomData] = useState<SymptomData[]>([]);
    const [timeSeriesData, setTimeSeriesData] = useState<TimeSeriesData[]>([]);
    const [selectedPeriod, setSelectedPeriod] = useState('7d');
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        loadDashboardData();
    }, [selectedPeriod]);

    const loadDashboardData = async () => {
        setIsLoading(true);

        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1500));

        // Mock data
        const mockStats: DashboardStats = {
            totalConsultations: 1247,
            emergencyAlerts: 23,
            activeUsers: 892,
            avgResponseTime: '2.3s'
        };

        const mockSymptoms: SymptomData[] = [
            { symptom: 'Fever', count: 342, percentage: 27.4 },
            { symptom: 'Headache', count: 298, percentage: 23.9 },
            { symptom: 'Cough', count: 234, percentage: 18.8 },
            { symptom: 'Stomach Pain', count: 189, percentage: 15.2 },
            { symptom: 'Fatigue', count: 156, percentage: 12.5 },
            { symptom: 'Chest Pain', count: 28, percentage: 2.2 }
        ];

        const mockTimeSeries: TimeSeriesData[] = [
            { date: '2024-01-01', consultations: 45, emergencies: 2 },
            { date: '2024-01-02', consultations: 52, emergencies: 1 },
            { date: '2024-01-03', consultations: 38, emergencies: 3 },
            { date: '2024-01-04', consultations: 61, emergencies: 0 },
            { date: '2024-01-05', consultations: 47, emergencies: 2 },
            { date: '2024-01-06', consultations: 55, emergencies: 1 },
            { date: '2024-01-07', consultations: 49, emergencies: 4 }
        ];

        setStats(mockStats);
        setSymptomData(mockSymptoms);
        setTimeSeriesData(mockTimeSeries);
        setIsLoading(false);
    };

    const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4'];

    const StatCard = ({ title, value, icon, color, subtitle }: any) => (
        <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 p-6">
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-sm font-medium text-gray-600">{title}</p>
                    <p className="text-3xl font-bold text-gray-900">{value}</p>
                    {subtitle && <p className="text-sm text-gray-500">{subtitle}</p>}
                </div>
                <div className={`p-3 rounded-full ${color}`}>
                    {icon}
                </div>
            </div>
        </div>
    );

    if (isLoading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center">
                <div className="text-center">
                    <Activity className="h-16 w-16 text-blue-500 mx-auto mb-4 animate-pulse" />
                    <h2 className="text-2xl font-bold text-gray-800 mb-2">Loading Analytics...</h2>
                    <p className="text-gray-600">Preparing your dashboard</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
            {/* Header */}
            <header className="bg-white/90 backdrop-blur-sm border-b border-gray-200/50 p-4">
                <div className="max-w-7xl mx-auto flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                        <Link
                            href="/"
                            className="flex items-center space-x-2 text-gray-600 hover:text-gray-800 transition-colors"
                        >
                            <ArrowLeft className="h-5 w-5" />
                            <span className="font-medium">Back to Home</span>
                        </Link>
                    </div>

                    <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2">
                            <BarChart className="h-6 w-6 text-blue-600" />
                            <span className="font-semibold text-blue-600">Analytics Dashboard</span>
                        </div>

                        <select
                            value={selectedPeriod}
                            onChange={(e) => setSelectedPeriod(e.target.value)}
                            className="bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            <option value="24h">Last 24 Hours</option>
                            <option value="7d">Last 7 Days</option>
                            <option value="30d">Last 30 Days</option>
                            <option value="90d">Last 90 Days</option>
                        </select>

                        <button className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                            <Download className="h-4 w-4" />
                            <span>Export</span>
                        </button>
                    </div>
                </div>
            </header>

            <div className="max-w-7xl mx-auto p-6">
                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    <StatCard
                        title="Total Consultations"
                        value={stats.totalConsultations.toLocaleString()}
                        icon={<Users className="h-6 w-6 text-white" />}
                        color="bg-blue-500"
                        subtitle={`${selectedPeriod} period`}
                    />

                    <StatCard
                        title="Emergency Alerts"
                        value={stats.emergencyAlerts}
                        icon={<AlertTriangle className="h-6 w-6 text-white" />}
                        color="bg-red-500"
                        subtitle="Requiring immediate attention"
                    />

                    <StatCard
                        title="Active Users"
                        value={stats.activeUsers.toLocaleString()}
                        icon={<Activity className="h-6 w-6 text-white" />}
                        color="bg-green-500"
                        subtitle="Currently online"
                    />

                    <StatCard
                        title="Avg Response Time"
                        value={stats.avgResponseTime}
                        icon={<Clock className="h-6 w-6 text-white" />}
                        color="bg-purple-500"
                        subtitle="AI consultation response"
                    />
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                    {/* Consultation Trends */}
                    <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 p-6">
                        <div className="flex items-center justify-between mb-6">
                            <h3 className="text-xl font-bold text-gray-800">Consultation Trends</h3>
                            <TrendingUp className="h-6 w-6 text-green-600" />
                        </div>

                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={timeSeriesData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                                <XAxis dataKey="date" stroke="#6b7280" fontSize={12} />
                                <YAxis stroke="#6b7280" fontSize={12} />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: 'white',
                                        border: '1px solid #e5e7eb',
                                        borderRadius: '8px'
                                    }}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="consultations"
                                    stroke="#3B82F6"
                                    strokeWidth={3}
                                    dot={{ fill: '#3B82F6', strokeWidth: 2, r: 4 }}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="emergencies"
                                    stroke="#EF4444"
                                    strokeWidth={3}
                                    dot={{ fill: '#EF4444', strokeWidth: 2, r: 4 }}
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Common Symptoms Distribution */}
                    <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 p-6">
                        <div className="flex items-center justify-between mb-6">
                            <h3 className="text-xl font-bold text-gray-800">Common Symptoms</h3>
                            <Heart className="h-6 w-6 text-red-600" />
                        </div>

                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie
                                    data={symptomData}
                                    cx="50%"
                                    cy="50%"
                                    outerRadius={100}
                                    fill="#8884d8"
                                    dataKey="count"
                                    label={({ symptom, percentage }) => `${symptom}: ${percentage}%`}
                                >
                                    {symptomData.map((_, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Detailed Symptom Analysis */}
                <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 p-6 mb-8">
                    <div className="flex items-center justify-between mb-6">
                        <h3 className="text-xl font-bold text-gray-800">Detailed Symptom Analysis</h3>
                        <Filter className="h-6 w-6 text-gray-600" />
                    </div>

                    <ResponsiveContainer width="100%" height={400}>
                        <BarChart data={symptomData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                            <XAxis dataKey="symptom" stroke="#6b7280" fontSize={12} />
                            <YAxis stroke="#6b7280" fontSize={12} />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: 'white',
                                    border: '1px solid #e5e7eb',
                                    borderRadius: '8px'
                                }}
                            />
                            <Bar dataKey="count" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>

                {/* Emergency Alerts Table */}
                <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 p-6">
                    <div className="flex items-center justify-between mb-6">
                        <h3 className="text-xl font-bold text-gray-800">Recent Emergency Alerts</h3>
                        <AlertTriangle className="h-6 w-6 text-red-600" />
                    </div>

                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-gray-200">
                                    <th className="text-left py-3 px-4 font-semibold text-gray-800">Time</th>
                                    <th className="text-left py-3 px-4 font-semibold text-gray-800">Symptoms</th>
                                    <th className="text-left py-3 px-4 font-semibold text-gray-800">Severity</th>
                                    <th className="text-left py-3 px-4 font-semibold text-gray-800">Location</th>
                                    <th className="text-left py-3 px-4 font-semibold text-gray-800">Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {[
                                    {
                                        time: '2 hours ago',
                                        symptoms: 'Severe chest pain, difficulty breathing',
                                        severity: 'Critical',
                                        location: 'Kampala Central',
                                        status: 'Responded'
                                    },
                                    {
                                        time: '4 hours ago',
                                        symptoms: 'Heavy bleeding, dizziness',
                                        severity: 'High',
                                        location: 'Entebbe',
                                        status: 'In Progress'
                                    },
                                    {
                                        time: '6 hours ago',
                                        symptoms: 'Severe allergic reaction',
                                        severity: 'Critical',
                                        location: 'Jinja',
                                        status: 'Resolved'
                                    }
                                ].map((alert, index) => (
                                    <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
                                        <td className="py-3 px-4 text-gray-700">{alert.time}</td>
                                        <td className="py-3 px-4 text-gray-700">{alert.symptoms}</td>
                                        <td className="py-3 px-4">
                                            <span className={`px-3 py-1 rounded-full text-sm font-medium ${alert.severity === 'Critical'
                                                    ? 'bg-red-100 text-red-800'
                                                    : 'bg-orange-100 text-orange-800'
                                                }`}>
                                                {alert.severity}
                                            </span>
                                        </td>
                                        <td className="py-3 px-4 text-gray-700">
                                            <div className="flex items-center space-x-1">
                                                <MapPin className="h-4 w-4 text-gray-400" />
                                                <span>{alert.location}</span>
                                            </div>
                                        </td>
                                        <td className="py-3 px-4">
                                            <span className={`px-3 py-1 rounded-full text-sm font-medium ${alert.status === 'Resolved'
                                                    ? 'bg-green-100 text-green-800'
                                                    : alert.status === 'Responded'
                                                        ? 'bg-blue-100 text-blue-800'
                                                        : 'bg-yellow-100 text-yellow-800'
                                                }`}>
                                                {alert.status}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
                    <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 p-6 text-center">
                        <Calendar className="h-12 w-12 text-blue-500 mx-auto mb-3" />
                        <h4 className="text-lg font-semibold text-gray-800 mb-2">Peak Hours</h4>
                        <p className="text-2xl font-bold text-blue-600">2-6 PM</p>
                        <p className="text-sm text-gray-500">Highest consultation volume</p>
                    </div>

                    <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 p-6 text-center">
                        <Users className="h-12 w-12 text-green-500 mx-auto mb-3" />
                        <h4 className="text-lg font-semibold text-gray-800 mb-2">User Satisfaction</h4>
                        <p className="text-2xl font-bold text-green-600">94.2%</p>
                        <p className="text-sm text-gray-500">Positive feedback rate</p>
                    </div>

                    <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 p-6 text-center">
                        <Activity className="h-12 w-12 text-purple-500 mx-auto mb-3" />
                        <h4 className="text-lg font-semibold text-gray-800 mb-2">System Uptime</h4>
                        <p className="text-2xl font-bold text-purple-600">99.8%</p>
                        <p className="text-sm text-gray-500">Last 30 days</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
