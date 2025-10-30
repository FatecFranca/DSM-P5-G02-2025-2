import mongoose, { Document, Schema } from 'mongoose';

export interface IDetection extends Document {
  userId: string;
  image?: string;  
  type?: 'text' | 'image' | string;
  // result is generic to support both text classification and image detection
  result: {
    // text classifier
    is_spam?: boolean | null;
    message?: string;
    // generic/vision
    confidence?: number;
    material?: string;
    reciclavel?: boolean;
    tipo?: string;
    // allow other keys if needed
    [key: string]: any;
  };
  status?: string;
  createdAt: Date;
}

const DetectionSchema: Schema = new Schema({
  userId: { type: String, required: true },
  image: { type: String },
  type: { type: String, default: 'text' },
  result: { type: Object, required: true },
  status: { type: String, default: 'sucesso' },
  createdAt: { type: Date, default: Date.now }
});

export default mongoose.model<IDetection>('Detection', DetectionSchema);