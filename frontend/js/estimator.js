const uiCoordinatesEstimator = {
  // Data has been collected manually as a base for estimation.
  //
  // Only a part of the interface is relevant here: On wider
  // screens this will be centered and left/right will be filled
  // up with empty placeholder space. We need to estimate
  // coordinates in relation to this area first, then map them to
  // absolute screen coordinates afterwards.
  //
  // All values below are absolute screen coordinates.

  sampleScreenWidth: 2560,
  sampleScreenHeight: 1080,

  // 1920x1080 centered on screen basically
  sampleAreaWidth: 1920,
  sampleAreaHeight: 1080,

  sampleAreaStartX: 320,
  sampleAreaEndX: 2240,

  sampleAreaStartY: 0,
  sampleAreaEndY: 1080,

  sampleUiCoordinates: {
    '1': {'x': '1810', 'y': '305'},
    '2': {'x': '1810', 'y': '455'},
    '3': {'x': '1810', 'y': '600'},
    '4': {'x': '1900', 'y': '600'},
    '5': {'x': '1990', 'y': '600'},
    '6': {'x': '2085', 'y': '600'},
    '7': {'x': '1810', 'y': '750'},
    '8': {'x': '1900', 'y': '750'},
    '9': {'x': '1990', 'y': '750'},
    '10': {'x': '2085', 'y': '750'},
    'search_box': {'x': '870', 'y': '230'},
    'first_item_in_list': {'x': '985', 'y': '310'},
    'remove_filters_button': {'x': '1660', 'y': '225'},
    // 'discard_item_dialog_yes_button': {'x': '1111', 'y': '732'},
  },
  estimate: function(width, height) {
    const estimatedUiCoordinates = {};

    const sampleAreaRatio = this.sampleAreaWidth / this.sampleAreaHeight;

    // Assuming always a landscape screen here (fillup height, scale width accordingly).
    const newAreaWidth = height * sampleAreaRatio;
    const newAreaHeight = height;

    // Find start and end points by centering area horizontally on screen.
    const newAreaStartX = (width - newAreaWidth) / 2;
    const newAreaEndX = width - newAreaStartX;

    const newAreaStartY = 0;
    const newAreaEndY = newAreaHeight;

    for (const key of Object.keys(this.sampleUiCoordinates)) {
      // Sample coordinates absolute to screen.
      const sampleX = this.sampleUiCoordinates[key].x;
      const sampleY = this.sampleUiCoordinates[key].y;

      const sampleAreaX = mapRange(
        this.sampleAreaStartX,
        this.sampleAreaEndX,
        0,
        this.sampleAreaWidth,
        sampleX
      );
      const sampleAreaY = mapRange(
        this.sampleAreaStartY,
        this.sampleAreaEndY,
        0,
        this.sampleAreaHeight,
        sampleY
      );

      const newAreaX = mapRange(
        0,
        this.sampleAreaWidth,
        0,
        newAreaWidth,
        sampleAreaX
      );
      const newAreaY = mapRange(
        0,
        this.sampleAreaHeight,
        0,
        newAreaHeight,
        sampleAreaY
      );

      const newAreaXOnScreen = mapRange(
        0,
        newAreaWidth,
        newAreaStartX,
        newAreaEndX,
        newAreaX
      );
      const newAreaYOnScreen = mapRange(
        0,
        newAreaHeight,
        newAreaStartY,
        newAreaEndY,
        newAreaY
      );

      const x = Math.round(newAreaXOnScreen);
      const y = Math.round(newAreaYOnScreen);

      estimatedUiCoordinates[key] = {"x": String(x), "y": String(y)};
    }

    return estimatedUiCoordinates;
  },
};
