import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, CheckCircle, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { api } from '@/services/api';
import { Spinner } from '@/components/ui/spinner';
import { motion } from 'framer-motion';

export default function Home() {
    const [file, setFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);
    const [resumeData, setResumeData] = useState<any>(null);
    const navigate = useNavigate();

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
        }
    };

    const handleUpload = async () => {
        if (!file) return;
        setUploading(true);
        try {
            const response = await api.uploadResume(file);
            if (response.status === 'success') {
                setResumeData(response.resume);
            }
        } catch (error) {
            console.error('Upload failed', error);
            alert('Upload failed. Please try again.');
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-[80vh] gap-8">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="text-center space-y-4 max-w-2xl"
            >
                <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl">
                    Your AI-Powered <span className="text-primary">Job Hunter</span>
                </h1>
                <p className="text-xl text-muted-foreground">
                    Upload your resume, set your preferences, and let AI find and tailor jobs for you.
                    Zero effort, maximum results.
                </p>
            </motion.div>

            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2, duration: 0.5 }}
                className="w-full max-w-md"
            >
                <Card className="border-2 border-dashed border-border/60 hover:border-primary/50 transition-colors">
                    <CardHeader>
                        <CardTitle>Upload Resume</CardTitle>
                        <CardDescription>PDF files only. We'll extract your skills and experience.</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {!resumeData ? (
                            <div className="flex flex-col gap-4">
                                <div className="grid w-full max-w-sm items-center gap-1.5">
                                    <div className="relative flex items-center justify-center h-32 rounded-md bg-muted/50 border-2 border-dashed border-muted-foreground/25 hover:bg-muted/70 transition-colors">
                                        <input
                                            type="file"
                                            accept=".pdf"
                                            onChange={handleFileChange}
                                            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                        />
                                        <div className="flex flex-col items-center gap-2 text-muted-foreground">
                                            {file ? (
                                                <>
                                                    <FileText className="h-8 w-8 text-primary" />
                                                    <span className="font-medium text-foreground">{file.name}</span>
                                                </>
                                            ) : (
                                                <>
                                                    <Upload className="h-8 w-8" />
                                                    <span>Click to upload or drag & drop</span>
                                                </>
                                            )}
                                        </div>
                                    </div>
                                </div>
                                <Button
                                    onClick={handleUpload}
                                    disabled={!file || uploading}
                                    className="w-full"
                                    size="lg"
                                >
                                    {uploading ? (
                                        <>
                                            <Spinner className="mr-2" /> Parsing Resume...
                                        </>
                                    ) : (
                                        "Upload & Analyze"
                                    )}
                                </Button>
                            </div>
                        ) : (
                            <div className="space-y-4">
                                <div className="flex items-center gap-4 p-4 rounded-lg bg-green-500/10 text-green-600 dark:text-green-400 border border-green-500/20">
                                    <CheckCircle className="h-6 w-6" />
                                    <div>
                                        <h3 className="font-semibold">Resume Analyzed!</h3>
                                        <p className="text-sm opacity-90">Welcome, {resumeData.full_name}</p>
                                    </div>
                                </div>
                                <Button
                                    onClick={() => navigate('/preferences')}
                                    className="w-full"
                                    size="lg"
                                >
                                    Continue to Preferences <ArrowRight className="ml-2 h-4 w-4" />
                                </Button>
                            </div>
                        )}
                    </CardContent>
                </Card>
            </motion.div>
        </div>
    );
}
