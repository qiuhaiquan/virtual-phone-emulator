// src/ext/camera_module/camera_module.h
#ifndef CAMERA_MODULE_H
#define CAMERA_MODULE_H

#include <opencv2/opencv.hpp>

class VirtualCamera {
private:
    cv::VideoCapture* camera;
    bool is_opened;

public:
    VirtualCamera(int camera_id);
    ~VirtualCamera();

    bool isOpened();
    cv::Mat captureFrame();
};

#endif // CAMERA_MODULE_H