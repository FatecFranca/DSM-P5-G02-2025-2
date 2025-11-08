import mongoose, { Document, Schema } from 'mongoose';

export interface IDetection extends Document {
  userId: string;
  type?: 'text' | string;
  // result for text classification
  result: {
    is_spam?: boolean | null;
    message?: string;
    confidence?: number;
    [key: string]: any;
  };
  status?: string;
  createdAt: Date;
}

const DetectionSchema: Schema = new Schema({
  userId: { type: String, required: true },
  type: { type: String, default: 'text' },
  result: { type: Object, required: true },
  status: { type: String, default: 'sucesso' },
  createdAt: { type: Date, default: Date.now }
});

export default mongoose.model<IDetection>('Detection', DetectionSchema);