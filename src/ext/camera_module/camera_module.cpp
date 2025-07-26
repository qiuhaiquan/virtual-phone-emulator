// src/ext/camera_module/camera_module.cpp
#include "camera_module.h"
#include <Python.h>
#include <opencv2/opencv.hpp>

// 实现VirtualCamera类
VirtualCamera::VirtualCamera(int camera_id) {
    camera = new cv::VideoCapture(camera_id);
    is_opened = camera->isOpened();
}

VirtualCamera::~VirtualCamera() {
    if (camera->isOpened()) {
        camera->release();
    }
    delete camera;
}

bool VirtualCamera::isOpened() {
    return is_opened;
}

cv::Mat VirtualCamera::captureFrame() {
    cv::Mat frame;
    if (is_opened) {
        *camera >> frame;
    }
    return frame;
}

// Python绑定代码
static PyObject* VirtualCamera_new(PyTypeObject* type, PyObject* args, PyObject* kwds) {
    VirtualCamera* self;
    self = (VirtualCamera*)type->tp_alloc(type, 0);
    if (self != NULL) {
        int camera_id = 0;
        if (!PyArg_ParseTuple(args, "i", &camera_id)) {
            Py_DECREF(self);
            return NULL;
        }
        self->camera = new VirtualCamera(camera_id);
    }
    return (PyObject*)self;
}

static void VirtualCamera_dealloc(VirtualCamera* self) {
    delete self->camera;
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject* VirtualCamera_isOpened(VirtualCamera* self, PyObject* args) {
    return PyBool_FromLong(self->camera->isOpened());
}

static PyObject* VirtualCamera_captureFrame(VirtualCamera* self, PyObject* args) {
    cv::Mat frame = self->camera->captureFrame();

    if (frame.empty()) {
        Py_RETURN_NONE;
    }

    // 这里需要实现将OpenCV的Mat转换为Python对象的逻辑
    // 简化示例，返回None
    Py_RETURN_NONE;
}

static PyMethodDef VirtualCamera_methods[] = {
    {"isOpened", (PyCFunction)VirtualCamera_isOpened, METH_NOARGS, "检查相机是否打开"},
    {"captureFrame", (PyCFunction)VirtualCamera_captureFrame, METH_NOARGS, "捕获一帧图像"},
    {NULL}  /* Sentinel */
};

static PyTypeObject VirtualCameraType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "camera_module.VirtualCamera",
    sizeof(VirtualCamera),
    0,
    (destructor)VirtualCamera_dealloc,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    "Virtual Camera Object",
    0,
    0,
    0,
    0,
    0,
    0,
    VirtualCamera_methods,
    0,
    0,
    0,
    0,
    0,
    0,
    VirtualCamera_new,
};

static PyModuleDef camera_module = {
    PyModuleDef_HEAD_INIT,
    "camera_module",
    "Virtual Camera Module",
    -1,
    NULL,
};

PyMODINIT_FUNC PyInit_camera_module(void) {
    PyObject* m;

    if (PyType_Ready(&VirtualCameraType) < 0)
        return NULL;

    m = PyModule_Create(&camera_module);
    if (m == NULL)
        return NULL;

    Py_INCREF(&VirtualCameraType);
    PyModule_AddObject(m, "VirtualCamera", (PyObject*)&VirtualCameraType);

    return m;
}