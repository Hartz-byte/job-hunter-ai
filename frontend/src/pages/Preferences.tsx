import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { api } from '@/services/api';
import { Spinner } from '@/components/ui/spinner';
import type { JobPreferences } from '@/types';
import { Plus, X, Briefcase } from 'lucide-react';

export default function Preferences() {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState<JobPreferences>({
        job_title: '',
        experience_level: 'mid',
        job_type: ['remote', 'hybrid'],
        locations: [],
        min_salary: 0,
        max_salary: 0,
        industries: [],
        required_skills: [],
        nice_to_have_skills: []
    });

    // Helper for array inputs
    const [skillInput, setSkillInput] = useState('');
    const [locationInput, setLocationInput] = useState('');

    const handleAddSkill = () => {
        if (skillInput.trim()) {
            setFormData(prev => ({ ...prev, required_skills: [...prev.required_skills, skillInput.trim()] }));
            setSkillInput('');
        }
    };

    const handleAddLocation = () => {
        if (locationInput.trim()) {
            setFormData(prev => ({ ...prev, locations: [...prev.locations, locationInput.trim()] }));
            setLocationInput('');
        }
    };

    const removeArrayItem = (key: keyof JobPreferences, index: number) => {
        // @ts-ignore
        setFormData(prev => ({ ...prev, [key]: prev[key].filter((_, i) => i !== index) }));
    };

    const handleSubmit = async () => {
        setLoading(true);
        try {
            await api.setPreferences(formData);
            navigate('/dashboard');
        } catch (error) {
            console.error('Failed to save preferences', error);
            alert('Failed to save preferences');
        } finally {
            setLoading(false);
        }
    };

    const toggleJobType = (type: string) => {
        setFormData(prev => {
            const types = prev.job_type.includes(type)
                ? prev.job_type.filter(t => t !== type)
                : [...prev.job_type, type];
            return { ...prev, job_type: types };
        });
    };

    return (
        <div className="max-w-3xl mx-auto space-y-6">
            <div className="space-y-2">
                <h1 className="text-3xl font-bold">Preferences</h1>
                <p className="text-muted-foreground">Tell us what kind of job you are looking for.</p>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Job Details</CardTitle>
                    <CardDescription>Narrow down your search.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                    <div className="grid gap-4 md:grid-cols-2">
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Job Title</label>
                            <Input
                                placeholder="e.g. Machine Learning Engineer"
                                value={formData.job_title}
                                onChange={e => setFormData({ ...formData, job_title: e.target.value })}
                            />
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium">Experience Level</label>
                            <select
                                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                                value={formData.experience_level}
                                onChange={e => setFormData({ ...formData, experience_level: e.target.value })}
                            >
                                <option value="entry">Entry Level</option>
                                <option value="mid">Mid Level</option>
                                <option value="senior">Senior Level</option>
                            </select>
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium">Job Type</label>
                        <div className="flex gap-2">
                            {['remote', 'hybrid', 'on-site'].map(type => (
                                <Badge
                                    key={type}
                                    variant={formData.job_type.includes(type) ? 'default' : 'outline'}
                                    className="cursor-pointer px-4 py-2 text-sm capitalize"
                                    onClick={() => toggleJobType(type)}
                                >
                                    {type}
                                </Badge>
                            ))}
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium">Locations</label>
                        <div className="flex gap-2">
                            <Input
                                placeholder="Add a location (e.g. San Francisco, Remote)"
                                value={locationInput}
                                onChange={e => setLocationInput(e.target.value)}
                                onKeyDown={e => e.key === 'Enter' && handleAddLocation()}
                            />
                            <Button onClick={handleAddLocation} size="icon"><Plus className="h-4 w-4" /></Button>
                        </div>
                        <div className="flex flex-wrap gap-2 mt-2">
                            {formData.locations.map((loc, i) => (
                                <Badge key={i} variant="secondary" className="pl-2 pr-1 py-1">
                                    {loc}
                                    <button onClick={() => removeArrayItem('locations', i)} className="ml-1 hover:text-destructive">
                                        <X className="h-3 w-3" />
                                    </button>
                                </Badge>
                            ))}
                        </div>
                    </div>

                    <div className="grid gap-4 md:grid-cols-2">
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Min Salary (Annual)</label>
                            <Input
                                type="number"
                                placeholder="0"
                                value={formData.min_salary}
                                onChange={e => setFormData({ ...formData, min_salary: Number(e.target.value) })}
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Max Salary (Annual)</label>
                            <Input
                                type="number"
                                placeholder="0"
                                value={formData.max_salary}
                                onChange={e => setFormData({ ...formData, max_salary: Number(e.target.value) })}
                            />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium">Required Skills</label>
                        <div className="flex gap-2">
                            <Input
                                placeholder="Add skill (e.g. PyTorch, TensorFlow, NLP)"
                                value={skillInput}
                                onChange={e => setSkillInput(e.target.value)}
                                onKeyDown={e => e.key === 'Enter' && handleAddSkill()}
                            />
                            <Button onClick={handleAddSkill} size="icon"><Plus className="h-4 w-4" /></Button>
                        </div>
                        <div className="flex flex-wrap gap-2 mt-2">
                            {formData.required_skills.map((skill, i) => (
                                <Badge key={i} variant="secondary" className="pl-2 pr-1 py-1">
                                    {skill}
                                    <button onClick={() => removeArrayItem('required_skills', i)} className="ml-1 hover:text-destructive">
                                        <X className="h-3 w-3" />
                                    </button>
                                </Badge>
                            ))}
                        </div>
                    </div>

                    <div className="pt-4">
                        <Button onClick={handleSubmit} className="w-full" size="lg" disabled={loading}>
                            {loading ? <Spinner className="mr-2" /> : <><Briefcase className="mr-2 h-4 w-4" /> Save & Find Jobs</>}
                        </Button>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
