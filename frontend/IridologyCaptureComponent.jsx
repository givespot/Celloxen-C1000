/**
 * CELLOXEN - IRIDOLOGY IMAGE CAPTURE COMPONENT
 * Captures left and right iris images for AI analysis
 * Created: November 14, 2025
 */

const IridologyCaptureComponent = ({ assessmentId, onComplete }) => {
    const [captureMethod, setCaptureMethod] = React.useState('camera'); // 'camera' or 'upload'
    const [currentEye, setCurrentEye] = React.useState('left'); // 'left' or 'right'
    const [leftEyeImage, setLeftEyeImage] = React.useState(null);
    const [rightEyeImage, setRightEyeImage] = React.useState(null);
    const [cameraActive, setCameraActive] = React.useState(false);
    const [analyzing, setAnalyzing] = React.useState(false);
    const [stream, setStream] = React.useState(null);
    
    const videoRef = React.useRef(null);
    const canvasRef = React.useRef(null);
    
    // Start camera
    const startCamera = async () => {
        try {
            const mediaStream = await navigator.mediaDevices.getUserMedia({
                video: { 
                    facingMode: 'user',
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                }
            });
            
            if (videoRef.current) {
                videoRef.current.srcObject = mediaStream;
                setStream(mediaStream);
                setCameraActive(true);
            }
        } catch (error) {
            alert('Could not access camera. Please allow camera permissions or use file upload.');
            console.error('Camera error:', error);
        }
    };
    
    // Stop camera
    const stopCamera = () => {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            setStream(null);
            setCameraActive(false);
        }
    };
    
    // Capture photo from camera
    const capturePhoto = () => {
        const canvas = canvasRef.current;
        const video = videoRef.current;
        
        if (canvas && video) {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0);
            
            // Convert to base64
            const imageData = canvas.toDataURL('image/jpeg', 0.8).split(',')[1];
            
            if (currentEye === 'left') {
                setLeftEyeImage(imageData);
                setCurrentEye('right');
            } else {
                setRightEyeImage(imageData);
                stopCamera();
            }
        }
    };
    
    // Handle file upload
    const handleFileUpload = (event, eye) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const base64 = e.target.result.split(',')[1];
                if (eye === 'left') {
                    setLeftEyeImage(base64);
                } else {
                    setRightEyeImage(base64);
                }
            };
            reader.readAsDataURL(file);
        }
    };
    
    // Submit to AI for analysis
    const submitForAnalysis = async () => {
        if (!leftEyeImage || !rightEyeImage) {
            alert('Please capture or upload both eye images');
            return;
        }
        
        setAnalyzing(true);
        
        try {
            const response = await fetch('/api/v1/iridology/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    assessment_id: assessmentId,
                    left_eye_image: leftEyeImage,
                    right_eye_image: rightEyeImage
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                alert('✅ Iridology analysis complete!');
                onComplete(data);
            } else {
                alert('Analysis failed. Please try again.');
            }
        } catch (error) {
            console.error('Analysis error:', error);
            alert('Error analyzing images. Please try again.');
        } finally {
            setAnalyzing(false);
        }
    };
    
    // Cleanup on unmount
    React.useEffect(() => {
        return () => stopCamera();
    }, []);
    
    return React.createElement('div', { className: 'max-w-4xl mx-auto p-6' },
        // Header
        React.createElement('div', { className: 'mb-8 text-center' },
            React.createElement('h2', { className: 'text-3xl font-bold text-gray-900 mb-2' }, 
                'Iridology Analysis'
            ),
            React.createElement('p', { className: 'text-gray-600' }, 
                'Capture high-quality images of both irises for AI-powered wellness analysis'
            )
        ),
        
        // Capture Method Selection
        React.createElement('div', { className: 'mb-8 flex gap-4 justify-center' },
            React.createElement('button', {
                onClick: () => setCaptureMethod('camera'),
                className: `px-6 py-3 rounded-lg ${captureMethod === 'camera' ? 'bg-purple-600 text-white' : 'bg-gray-200 text-gray-700'}`
            }, '📷 Use Camera'),
            React.createElement('button', {
                onClick: () => setCaptureMethod('upload'),
                className: `px-6 py-3 rounded-lg ${captureMethod === 'upload' ? 'bg-purple-600 text-white' : 'bg-gray-200 text-gray-700'}`
            }, '📁 Upload Files')
        ),
        
        // Camera Capture Mode
        captureMethod === 'camera' && React.createElement('div', { className: 'mb-8' },
            // Current Eye Indicator
            React.createElement('div', { className: 'mb-4 p-4 bg-blue-50 rounded-lg text-center' },
                React.createElement('p', { className: 'text-lg font-semibold' },
                    currentEye === 'left' ? '👁️ Capturing Left Eye' : '👁️ Capturing Right Eye'
                )
            ),
            
            // Video/Canvas
            React.createElement('div', { className: 'relative bg-black rounded-lg overflow-hidden mb-4' },
                React.createElement('video', {
                    ref: videoRef,
                    autoPlay: true,
                    playsInline: true,
                    className: 'w-full'
                }),
                React.createElement('canvas', {
                    ref: canvasRef,
                    className: 'hidden'
                })
            ),
            
            // Camera Controls
            React.createElement('div', { className: 'flex gap-4 justify-center' },
                !cameraActive && React.createElement('button', {
                    onClick: startCamera,
                    className: 'px-8 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700'
                }, 'Start Camera'),
                
                cameraActive && React.createElement('button', {
                    onClick: capturePhoto,
                    className: 'px-8 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700'
                }, `Capture ${currentEye === 'left' ? 'Left' : 'Right'} Eye`),
                
                cameraActive && React.createElement('button', {
                    onClick: stopCamera,
                    className: 'px-8 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700'
                }, 'Stop Camera')
            )
        ),
        
        // File Upload Mode
        captureMethod === 'upload' && React.createElement('div', { className: 'mb-8 space-y-6' },
            // Left Eye Upload
            React.createElement('div', { className: 'border-2 border-dashed border-gray-300 rounded-lg p-6' },
                React.createElement('label', { className: 'block text-center cursor-pointer' },
                    React.createElement('div', { className: 'mb-4' },
                        React.createElement('p', { className: 'text-lg font-semibold mb-2' }, '👁️ Left Eye'),
                        leftEyeImage ? 
                            React.createElement('p', { className: 'text-green-600' }, '✅ Image uploaded') :
                            React.createElement('p', { className: 'text-gray-600' }, 'Click to upload left eye image')
                    ),
                    React.createElement('input', {
                        type: 'file',
                        accept: 'image/*',
                        onChange: (e) => handleFileUpload(e, 'left'),
                        className: 'hidden'
                    })
                )
            ),
            
            // Right Eye Upload
            React.createElement('div', { className: 'border-2 border-dashed border-gray-300 rounded-lg p-6' },
                React.createElement('label', { className: 'block text-center cursor-pointer' },
                    React.createElement('div', { className: 'mb-4' },
                        React.createElement('p', { className: 'text-lg font-semibold mb-2' }, '👁️ Right Eye'),
                        rightEyeImage ? 
                            React.createElement('p', { className: 'text-green-600' }, '✅ Image uploaded') :
                            React.createElement('p', { className: 'text-gray-600' }, 'Click to upload right eye image')
                    ),
                    React.createElement('input', {
                        type: 'file',
                        accept: 'image/*',
                        onChange: (e) => handleFileUpload(e, 'right'),
                        className: 'hidden'
                    })
                )
            )
        ),
        
        // Image Preview
        (leftEyeImage || rightEyeImage) && React.createElement('div', { className: 'mb-8 grid grid-cols-2 gap-4' },
            leftEyeImage && React.createElement('div', { className: 'text-center' },
                React.createElement('p', { className: 'font-semibold mb-2' }, 'Left Eye'),
                React.createElement('img', {
                    src: `data:image/jpeg;base64,${leftEyeImage}`,
                    alt: 'Left Eye',
                    className: 'w-full rounded-lg border-2 border-gray-300'
                })
            ),
            rightEyeImage && React.createElement('div', { className: 'text-center' },
                React.createElement('p', { className: 'font-semibold mb-2' }, 'Right Eye'),
                React.createElement('img', {
                    src: `data:image/jpeg;base64,${rightEyeImage}`,
                    alt: 'Right Eye',
                    className: 'w-full rounded-lg border-2 border-gray-300'
                })
            )
        ),
        
        // Submit Button
        (leftEyeImage && rightEyeImage) && React.createElement('div', { className: 'text-center' },
            React.createElement('button', {
                onClick: submitForAnalysis,
                disabled: analyzing,
                className: 'px-12 py-4 bg-purple-600 text-white text-lg font-semibold rounded-lg hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed'
            }, analyzing ? '🔄 Analyzing with AI...' : '✨ Analyze with AI')
        )
    );
};

// Export for use in other components
window.IridologyCaptureComponent = IridologyCaptureComponent;
