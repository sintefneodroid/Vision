package dk.aivclab.demo.usecases.detection;

class Constants {
  static final String TAG = "AIVCLabDemo";
  static final String FORMAT_MS = "%dms";
  static final String FORMAT_AVG_MS = "avg:%.0fms";
  static final String FORMAT_FPS = "%.1fFPS";

  static final String SCORES_FORMAT = "%.2f";
  static final int INPUT_TENSOR_WIDTH = 224;
  static final int INPUT_TENSOR_HEIGHT = 224;
  static final int MOVING_AVG_PERIOD = 10;

  static final String MODEL_NAME = "detectnet.pt";
}