#!/usr/bin/env python3
"""
Document Understanding Dataset

Dataset class for loading and preprocessing PDF documents
with layout and entity annotations for training.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import torch
from torch.utils.data import Dataset
from PIL import Image
import yaml

logger = logging.getLogger(__name__)


class DocumentDataset(Dataset):
    """
    Dataset for document understanding training.
    
    Expected directory structure:
        data_dir/
        ├── documents/
        │   ├── doc_001.pdf
        │   ├── doc_001.png  # Rendered page image
        │   └── ...
        ├── annotations/
        │   ├── doc_001.json
        │   └── ...
        └── manifest.json
        
    Annotation format:
    {
        "document_id": "doc_001",
        "pages": [
            {
                "page_num": 1,
                "image": "doc_001_p1.png",
                "width": 612,
                "height": 792,
                "segments": [
                    {
                        "type": "header",
                        "bbox": [x1, y1, x2, y2],
                        "text": "Invoice #12345"
                    }
                ],
                "entities": [
                    {
                        "type": "INVOICE_NUMBER",
                        "text": "12345",
                        "bbox": [x1, y1, x2, y2]
                    }
                ]
            }
        ]
    }
    """
    
    # Segment type to ID mapping
    SEGMENT_TYPES = {
        'header': 0,
        'subheader': 1,
        'paragraph': 2,
        'table': 3,
        'table_row': 4,
        'table_cell': 5,
        'form_field': 6,
        'form_value': 7,
        'list_item': 8,
        'figure': 9,
        'footer': 10,
        'signature': 11,
        'other': 12
    }
    
    # Entity type to ID mapping
    ENTITY_TYPES = {
        'O': 0,  # Outside any entity
        'DATE': 1,
        'AMOUNT': 2,
        'CURRENCY': 3,
        'PERSON': 4,
        'ORGANIZATION': 5,
        'ADDRESS': 6,
        'PHONE': 7,
        'EMAIL': 8,
        'ID_NUMBER': 9,
        'PERCENTAGE': 10
    }
    
    def __init__(
        self,
        data_dir: str,
        transform: Optional[Any] = None,
        max_length: int = 512,
        image_size: int = 1024
    ):
        """
        Initialize the dataset.
        
        Args:
            data_dir: Path to dataset directory
            transform: Optional image transforms
            max_length: Maximum sequence length for text
            image_size: Size to resize images to
        """
        self.data_dir = Path(data_dir)
        self.transform = transform
        self.max_length = max_length
        self.image_size = image_size
        
        # Load manifest
        self.samples = self._load_manifest()
        logger.info(f"Loaded {len(self.samples)} samples from {data_dir}")
        
    def _load_manifest(self) -> List[Dict[str, Any]]:
        """Load dataset manifest."""
        manifest_path = self.data_dir / 'manifest.json'
        
        if manifest_path.exists():
            with open(manifest_path, 'r') as f:
                return json.load(f)
        else:
            # Auto-discover annotations
            annotations_dir = self.data_dir / 'annotations'
            samples = []
            
            for ann_file in annotations_dir.glob('*.json'):
                with open(ann_file, 'r') as f:
                    ann = json.load(f)
                    samples.append(ann)
                    
            return samples
    
    def __len__(self) -> int:
        return len(self.samples)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """
        Get a single sample.
        
        Returns:
            Dictionary containing:
            - image: Tensor of shape (C, H, W)
            - input_ids: Token IDs
            - attention_mask: Attention mask
            - bbox: Bounding boxes for each token
            - segment_labels: Segment type for each token
            - entity_labels: Entity type for each token
        """
        sample = self.samples[idx]
        
        # Load first page (for now, single-page training)
        page = sample['pages'][0]
        
        # Load image
        image_path = self.data_dir / 'documents' / page['image']
        image = self._load_image(image_path)
        
        # Process annotations
        segments = page.get('segments', [])
        entities = page.get('entities', [])
        
        # Tokenize and create labels
        tokens, bboxes = self._tokenize_segments(segments)
        segment_labels = self._create_segment_labels(segments, tokens)
        entity_labels = self._create_entity_labels(entities, tokens, bboxes)
        
        # Pad or truncate to max_length
        tokens, bboxes, segment_labels, entity_labels = self._pad_or_truncate(
            tokens, bboxes, segment_labels, entity_labels
        )
        
        return {
            'image': image,
            'input_ids': torch.tensor(tokens, dtype=torch.long),
            'bbox': torch.tensor(bboxes, dtype=torch.long),
            'segment_labels': torch.tensor(segment_labels, dtype=torch.long),
            'entity_labels': torch.tensor(entity_labels, dtype=torch.long),
            'attention_mask': torch.ones(len(tokens), dtype=torch.long)
        }
    
    def _load_image(self, path: Path) -> torch.Tensor:
        """Load and preprocess image."""
        image = Image.open(path).convert('RGB')
        
        # Resize
        image = image.resize((self.image_size, self.image_size))
        
        # Apply transforms
        if self.transform:
            image = self.transform(image)
        else:
            # Default: convert to tensor and normalize
            import torchvision.transforms as T
            transform = T.Compose([
                T.ToTensor(),
                T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
            image = transform(image)
            
        return image
    
    def _tokenize_segments(
        self, 
        segments: List[Dict]
    ) -> Tuple[List[int], List[List[int]]]:
        """
        Tokenize text from segments.
        
        Returns:
            Tuple of (token_ids, bboxes)
        """
        # TODO: Use actual tokenizer (e.g., LayoutLMv3Tokenizer)
        # This is a placeholder implementation
        
        tokens = []
        bboxes = []
        
        for segment in segments:
            text = segment.get('text', '')
            bbox = segment.get('bbox', [0, 0, 0, 0])
            
            # Simple word tokenization (placeholder)
            words = text.split()
            for word in words:
                # Placeholder token ID
                tokens.append(hash(word) % 30000)
                bboxes.append(bbox)
        
        return tokens, bboxes
    
    def _create_segment_labels(
        self, 
        segments: List[Dict], 
        tokens: List[int]
    ) -> List[int]:
        """Create segment labels for each token."""
        labels = []
        
        for segment in segments:
            seg_type = segment.get('type', 'other')
            label = self.SEGMENT_TYPES.get(seg_type, self.SEGMENT_TYPES['other'])
            
            # One label per word in segment
            num_words = len(segment.get('text', '').split())
            labels.extend([label] * num_words)
        
        return labels
    
    def _create_entity_labels(
        self,
        entities: List[Dict],
        tokens: List[int],
        bboxes: List[List[int]]
    ) -> List[int]:
        """Create entity labels for each token using BIO tagging."""
        # Start with all O (Outside) labels
        labels = [self.ENTITY_TYPES['O']] * len(tokens)
        
        # TODO: Implement proper BIO tagging based on bbox overlap
        # This is a placeholder
        
        return labels
    
    def _pad_or_truncate(
        self,
        tokens: List[int],
        bboxes: List[List[int]],
        segment_labels: List[int],
        entity_labels: List[int]
    ) -> Tuple[List[int], List[List[int]], List[int], List[int]]:
        """Pad or truncate sequences to max_length."""
        
        if len(tokens) > self.max_length:
            # Truncate
            tokens = tokens[:self.max_length]
            bboxes = bboxes[:self.max_length]
            segment_labels = segment_labels[:self.max_length]
            entity_labels = entity_labels[:self.max_length]
        else:
            # Pad
            pad_length = self.max_length - len(tokens)
            tokens.extend([0] * pad_length)
            bboxes.extend([[0, 0, 0, 0]] * pad_length)
            segment_labels.extend([0] * pad_length)
            entity_labels.extend([0] * pad_length)
            
        return tokens, bboxes, segment_labels, entity_labels


def create_dataloader(
    data_dir: str,
    batch_size: int = 8,
    shuffle: bool = True,
    num_workers: int = 4,
    **kwargs
) -> torch.utils.data.DataLoader:
    """
    Create a DataLoader for the document dataset.
    
    Args:
        data_dir: Path to dataset directory
        batch_size: Batch size
        shuffle: Whether to shuffle
        num_workers: Number of data loading workers
        **kwargs: Additional arguments for DocumentDataset
        
    Returns:
        DataLoader instance
    """
    dataset = DocumentDataset(data_dir, **kwargs)
    
    return torch.utils.data.DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=True
    )
