import axios from 'axios';
import type { JobPreferences } from '../types';

const API_Base = 'http://localhost:8000/api';

export const api = {
    uploadResume: async (file: File) => {
        const formData = new FormData();
        formData.append('file', file);
        const response = await axios.post(`${API_Base}/resume/upload`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
        return response.data;
    },

    setPreferences: async (preferences: JobPreferences) => {
        const response = await axios.post(`${API_Base}/preferences/set`, preferences);
        return response.data;
    },

    getUser: async () => {
        const response = await axios.get(`${API_Base}/user/me`);
        return response.data;
    },

    searchJobs: async (query: string, filters: any = {}) => {
        const params = new URLSearchParams({ query, ...filters });
        const response = await axios.post(`${API_Base}/jobs/search?${params.toString()}`);
        return response.data;
    },

    matchJobs: async (query: string, limit: number = 10) => {
        const response = await axios.post(`${API_Base}/jobs/match?query=${query}&limit=${limit}`);
        return response.data;
    },

    generateResume: async (jobTitle: string) => {
        const response = await axios.post(`${API_Base}/resume/generate?job_title=${jobTitle}`);
        return response.data;
    },

    generateCoverLetter: async (jobTitle: string, companyName: string) => {
        const response = await axios.post(
            `${API_Base}/cover-letter/generate?job_title=${jobTitle}&company_name=${companyName}`
        );
        return response.data;
    }
};
