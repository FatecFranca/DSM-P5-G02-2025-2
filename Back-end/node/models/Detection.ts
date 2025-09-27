import mongoose, { Document, Schema } from 'mongoose';

export interface IDetection extends Document {
  userId: string;
  image: string;  
  result: {
    confidence: number;
    material: string;
    reciclavel: boolean;
    tipo: string;
  };
  status: string;
  createdAt: Date;
}

const DetectionSchema: Schema = new Schema({
  userId: { type: String, required: true },
  image: { type: String, required: true },
  result: { type: Object, required: true },
  status: { type: String, default: 'sucesso' },
  createdAt: { type: Date, default: Date.now }
});

export default mongoose.model<IDetection>('Detection', DetectionSchema);