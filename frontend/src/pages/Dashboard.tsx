import { useState } from 'react';
import { api } from '@/services/api';
import type { Job, MatchResult } from '@/types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Spinner } from '@/components/ui/spinner';
import { Search, MapPin, Briefcase, Building, Calendar, CheckSquare, Square, FileText, Download, DollarSign, ArrowRight } from 'lucide-react';
import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';

export default function Dashboard() {
    const [query, setQuery] = useState('');
    const [loading, setLoading] = useState(false);
    const [jobs, setJobs] = useState<MatchResult[]>([]);
    const [selectedJobIds, setSelectedJobIds] = useState<Set<string>>(new Set());
    const [activeJob, setActiveJob] = useState<Job | null>(null);
    const [generating, setGenerating] = useState<{ [key: string]: boolean }>({});

    const handleSearch = async () => {
        if (!query.trim()) return;
        setLoading(true);
        setJobs([]);
        setActiveJob(null);
        try {
            // First search, then match
            const response = await api.matchJobs(query);
            if (response.status === 'success') {
                setJobs(response.jobs);
                if (response.jobs.length > 0) {
                    setActiveJob(response.jobs[0].job);
                }
            }
        } catch (error) {
            console.error('Search failed', error);
            alert('Search failed');
        } finally {
            setLoading(false);
        }
    };

    const toggleSelection = (id: string, e: React.MouseEvent) => {
        e.stopPropagation();
        const newSelected = new Set(selectedJobIds);
        if (newSelected.has(id)) {
            newSelected.delete(id);
        } else {
            newSelected.add(id);
        }
        setSelectedJobIds(newSelected);
    };

    const generateResume = async (job: Job) => {
        setGenerating(prev => ({ ...prev, [`resume-${job.id}`]: true }));
        try {
            const response = await api.generateResume(job.title);
            if (response.status === 'success') {
                window.open(`http://localhost:8000${response.download_url}`, '_blank');
            }
        } catch (e) {
            alert(`Failed to generate resume for ${job.title}`);
        } finally {
            setGenerating(prev => ({ ...prev, [`resume-${job.id}`]: false }));
        }
    };

    const generateCoverLetter = async (job: Job) => {
        setGenerating(prev => ({ ...prev, [`letter-${job.id}`]: true }));
        try {
            const response = await api.generateCoverLetter(job.title, job.company);
            if (response.status === 'success') {
                window.open(`http://localhost:8000${response.download_url}`, '_blank');
            }
        } catch (e) {
            alert(`Failed to generate cover letter for ${job.title}`);
        } finally {
            setGenerating(prev => ({ ...prev, [`letter-${job.id}`]: false }));
        }
    };

    const generateForSelected = async (type: 'resume' | 'letter') => {
        const selectedJobs = jobs.filter(j => selectedJobIds.has(j.job.id)).map(j => j.job);
        for (const job of selectedJobs) {
            if (type === 'resume') await generateResume(job);
            else await generateCoverLetter(job);
        }
    };

    return (
        <div className="flex flex-col h-[calc(100vh-8rem)] gap-4">
            {/* Search Bar */}
            <div className="flex items-center gap-4 p-1">
                <div className="relative flex-1">
                    <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input
                        placeholder="Search for jobs (e.g. React Developer in Bangalore)..."
                        className="pl-8"
                        value={query}
                        onChange={e => setQuery(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && handleSearch()}
                    />
                </div>
                <Button onClick={handleSearch} disabled={loading}>
                    {loading ? <Spinner className="mr-2" /> : "Find Jobs"}
                </Button>
            </div>

            <div className="flex flex-1 gap-6 overflow-hidden">
                {/* Job List */}
                <div className="w-1/3 flex flex-col gap-4 overflow-y-auto pr-2">
                    {jobs.length === 0 && !loading && (
                        <div className="text-center text-muted-foreground py-10">
                            No jobs found. Try a different search.
                        </div>
                    )}

                    {loading && (
                        <div className="flex justify-center py-10">
                            <Spinner className="h-8 w-8 text-primary" />
                        </div>
                    )}

                    {jobs.map((item) => (
                        <div
                            key={item.job.id}
                            onClick={() => setActiveJob(item.job)}
                            className={cn(
                                "p-4 rounded-lg border cursor-pointer transition-all hover:bg-accent",
                                activeJob?.id === item.job.id ? "border-primary bg-accent/50" : "border-border",
                                "relative group"
                            )}
                        >
                            <div className="absolute top-4 right-4 z-10" onClick={(e) => toggleSelection(item.job.id, e)}>
                                {selectedJobIds.has(item.job.id) ? (
                                    <CheckSquare className="h-5 w-5 text-primary" />
                                ) : (
                                    <Square className="h-5 w-5 text-muted-foreground opacity-50 group-hover:opacity-100" />
                                )}
                            </div>

                            <h3 className="font-semibold pr-8 truncate">{item.job.title}</h3>
                            <div className="text-sm text-muted-foreground truncate">{item.job.company}</div>

                            <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
                                <Badge variant="secondary" className={cn(
                                    item.match_score > 80 ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300" :
                                        item.match_score > 50 ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300" :
                                            "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300"
                                )}>
                                    {item.match_score}% Match
                                </Badge>
                                <span className="flex items-center"><MapPin className="h-3 w-3 mr-1" /> {item.job.location}</span>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Job Details */}
                <div className="flex-1 rounded-lg border bg-card text-card-foreground shadow-sm overflow-hidden flex flex-col">
                    {activeJob ? (
                        <>
                            <div className="p-6 border-b bg-muted/20">
                                <div className="flex justify-between items-start">
                                    <div>
                                        <h2 className="text-2xl font-bold">{activeJob.title}</h2>
                                        <div className="flex items-center gap-2 text-lg text-muted-foreground mt-1">
                                            <Building className="h-5 w-5" />
                                            {activeJob.company}
                                        </div>
                                    </div>
                                    <div className="flex gap-2">
                                        <Button
                                            size="sm"
                                            variant="outline"
                                            onClick={() => generateCoverLetter(activeJob)}
                                            disabled={generating[`letter-${activeJob.id}`]}
                                        >
                                            {generating[`letter-${activeJob.id}`] ? <Spinner className="mr-2" /> : <FileText className="mr-2 h-4 w-4" />}
                                            Cover Letter
                                        </Button>
                                        <Button
                                            size="sm"
                                            onClick={() => generateResume(activeJob)}
                                            disabled={generating[`resume-${activeJob.id}`]}
                                        >
                                            {generating[`resume-${activeJob.id}`] ? <Spinner className="mr-2" /> : <Download className="mr-2 h-4 w-4" />}
                                            Tailored Resume
                                        </Button>
                                    </div>
                                </div>

                                <div className="flex flex-wrap gap-4 mt-6 text-sm">
                                    <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-background border">
                                        <MapPin className="h-4 w-4 text-muted-foreground" />
                                        {activeJob.location}
                                    </div>
                                    <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-background border">
                                        <Briefcase className="h-4 w-4 text-muted-foreground" />
                                        {activeJob.job_type || "Full-time"}
                                    </div>
                                    {activeJob.salary && (
                                        <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-background border">
                                            <DollarSign className="h-4 w-4 text-muted-foreground" />
                                            {activeJob.salary}
                                        </div>
                                    )}
                                    <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-background border">
                                        <Calendar className="h-4 w-4 text-muted-foreground" />
                                        Posted: {new Date(activeJob.posted_date).toLocaleDateString()}
                                    </div>
                                </div>
                            </div>

                            <div className="p-6 overflow-y-auto flex-1 whitespace-pre-wrap font-sans leading-relaxed">
                                <h3 className="font-semibold mb-2">Description</h3>
                                {activeJob.description}

                                <div className="mt-8 pt-4 border-t">
                                    <a href={activeJob.url} target="_blank" rel="noreferrer">
                                        <Button variant="link" className="px-0">View Original Post <ArrowRight className="ml-2 h-4 w-4" /></Button>
                                    </a>
                                </div>
                            </div>
                        </>
                    ) : (
                        <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
                            <Briefcase className="h-12 w-12 mb-4 opacity-20" />
                            <p>Select a job to view details</p>
                        </div>
                    )}
                </div>
            </div>

            {/* Bulk Actions Floating Bar */}
            <AnimatePresence>
                {selectedJobIds.size > 0 && (
                    <motion.div
                        initial={{ y: 100, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        exit={{ y: 100, opacity: 0 }}
                        className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-foreground text-background px-6 py-3 rounded-full shadow-lg flex items-center gap-4 z-50"
                    >
                        <span className="font-medium">{selectedJobIds.size} jobs selected</span>
                        <div className="h-4 w-px bg-background/20" />
                        <Button
                            size="sm"
                            variant="secondary"
                            onClick={() => generateForSelected('resume')}
                            className="h-8"
                        >
                            Generate Resumes
                        </Button>
                        <Button
                            size="sm"
                            variant="secondary"
                            onClick={() => generateForSelected('letter')}
                            className="h-8"
                        >
                            Generate Cover Letters
                        </Button>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
