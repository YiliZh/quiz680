export interface Upload {
  id: number;
  filename: string;
  title: string;
  description?: string;
  status: string;
  user_id: number;
  uploaded_at: string;
  chapters?: any[];
} 