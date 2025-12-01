"""Pet detection service using YOLO for validating pet presence in images/videos."""

import logging
from typing import List, Optional, Tuple
from io import BytesIO

import httpx
from PIL import Image
import numpy as np

_logger = logging.getLogger(__name__)


class PetDetectionService:
    """
    Service to detect pets (dogs, cats, birds, etc.) in images or videos.
    Uses YOLOv5 for object detection or can integrate with custom CV models.
    """

    # COCO dataset classes for common pets
    PET_CLASSES = {
        "dog": 16,
        "cat": 15,
        "bird": 14,
        "horse": 17,
        "sheep": 18,
        "cow": 19,
        "elephant": 20,
        "bear": 21,
        "zebra": 22,
        "giraffe": 23,
    }

    def __init__(self, model_name: str = "yolov5s", confidence_threshold: float = 0.5):
        """
        Initialize pet detection service.

        Args:
            model_name: YOLO model to use (yolov5s, yolov5m, yolov5l, yolov5x)
            confidence_threshold: Minimum confidence score for detections (0.0-1.0)
        """
        self.model_name = model_name
        self.confidence_threshold = confidence_threshold
        self._model = None
        self._initialized = False

    def _lazy_load_model(self):
        """Lazy load the YOLO model on first use to save memory."""
        if not self._initialized:
            try:
                import torch
                _logger.info(f"Loading YOLO model: {self.model_name}")
                self._model = torch.hub.load('ultralytics/yolov5', self.model_name, pretrained=True)
                self._model.conf = self.confidence_threshold
                self._initialized = True
                _logger.info("✅ YOLO model loaded successfully")
            except Exception as e:
                _logger.error(f"Failed to load YOLO model: {e}")
                raise RuntimeError(f"Could not initialize pet detection model: {e}")

    async def detect_pets_in_image_url(
        self,
        image_url: str,
        http_client: httpx.AsyncClient
    ) -> Tuple[bool, List[str], Optional[Image.Image]]:
        """
        Download and analyze an image URL for pet presence.

        Args:
            image_url: URL of the image to analyze
            http_client: HTTP client for downloading the image

        Returns:
            Tuple of (has_pets, detected_pets_list, image)
            - has_pets: Boolean indicating if any pets were detected
            - detected_pets_list: List of detected pet types (e.g., ["dog", "cat"])
            - image: PIL Image object (None if download failed)
        """
        try:
            response = await http_client.get(image_url, timeout=10.0)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content))
            return await self.detect_pets_in_image(image)
        except Exception as e:
            _logger.error(f"Failed to download/process image from {image_url}: {e}")
            return False, [], None

    async def detect_pets_in_image(
        self,
        image: Image.Image
    ) -> Tuple[bool, List[str], Image.Image]:
        """
        Analyze a PIL Image for pet presence using YOLO.

        Args:
            image: PIL Image to analyze

        Returns:
            Tuple of (has_pets, detected_pets_list, image)
        """
        self._lazy_load_model()

        try:
            # Convert PIL Image to numpy array for YOLO
            img_array = np.array(image.convert('RGB'))

            # Run inference
            results = self._model(img_array)

            # Parse detections
            detected_pets = []
            detections = results.pandas().xyxy[0]  # Get pandas DataFrame of detections

            for _, detection in detections.iterrows():
                class_id = int(detection['class'])
                confidence = float(detection['confidence'])
                class_name = detection['name'].lower()

                # Check if detected object is a pet
                if class_name in self.PET_CLASSES.keys() and confidence >= self.confidence_threshold:
                    if class_name not in detected_pets:
                        detected_pets.append(class_name)
                    _logger.info(f"Detected {class_name} with confidence {confidence:.2f}")

            has_pets = len(detected_pets) > 0

            if has_pets:
                _logger.info(f"✅ Pets detected: {', '.join(detected_pets)}")
            else:
                _logger.warning("⚠️  No pets detected in image")

            return has_pets, detected_pets, image

        except Exception as e:
            _logger.error(f"Pet detection failed: {e}")
            # Return False to be safe - don't process if detection fails
            return False, [], image

    async def detect_pets_in_base64(
        self,
        base64_image: str
    ) -> Tuple[bool, List[str], Optional[Image.Image]]:
        """
        Analyze a base64-encoded image for pet presence.

        Args:
            base64_image: Base64 encoded image string

        Returns:
            Tuple of (has_pets, detected_pets_list, image)
        """
        try:
            import base64
            image_data = base64.b64decode(base64_image)
            image = Image.open(BytesIO(image_data))
            return await self.detect_pets_in_image(image)
        except Exception as e:
            _logger.error(f"Failed to decode base64 image: {e}")
            return False, [], None

    def get_detection_stats(self) -> dict:
        """Return statistics about the detection service."""
        return {
            "model_name": self.model_name,
            "confidence_threshold": self.confidence_threshold,
            "initialized": self._initialized,
            "supported_pets": list(self.PET_CLASSES.keys()),
        }


# Global singleton instance (lazy initialized)
_pet_detector: Optional[PetDetectionService] = None


def get_pet_detector(
    model_name: str = "yolov5s",
    confidence_threshold: float = 0.5
) -> PetDetectionService:
    """Get or create the global pet detection service instance."""
    global _pet_detector
    if _pet_detector is None:
        _pet_detector = PetDetectionService(
            model_name=model_name,
            confidence_threshold=confidence_threshold
        )
    return _pet_detector
