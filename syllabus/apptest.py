
from app import Syllabus


if __name__ == '__main__':

    s = Syllabus()
    s.log = """
----------------------------------------------------------------------------------------------------------

                                 Random Feature Support Vector Classifier

----------------------------------------------------------------------------------------------------------

    +---------+-----+------------------------------------------------------------+
    |Parameter|Value|Description                                                 |
    +---------+-----+------------------------------------------------------------+
    |ptrain   |0.1  |Percent of training images to use (default=0.01)            |
    +---------+-----+------------------------------------------------------------+
    |ptest    |1.0  |Percent of test images to use (default=0.1)                 |
    +---------+-----+------------------------------------------------------------+
    |fdim     |2500 |Feature space dimensionality (default=5000)                 |
    +---------+-----+------------------------------------------------------------+
    |knn      |False|Use Color k-means? (default=False)                          |
    +---------+-----+------------------------------------------------------------+
    |k        |5    |Number of means to use (default=5)                          |
    +---------+-----+------------------------------------------------------------+
    |kernel   |G    |Kernel type ("G", "L", or "C") (default=G)                  |
    +---------+-----+------------------------------------------------------------+
    |ntrain   |-25  |Number of patients used for training (default=-25)          |
    +---------+-----+------------------------------------------------------------+
    |ntest    |25   |Number of patients used for testing (default=25)            |
    +---------+-----+------------------------------------------------------------+
    |cores    |8    |Number of cores (processes) to use (8 available) (default=8)|
    +---------+-----+------------------------------------------------------------+
    |ftype    |F    |Type of feature to use ("F" or "B") (default=F)             |
    +---------+-----+------------------------------------------------------------+


-- Main Program ------------------------------------------------------------------------------------------
<RF> Random Feature Support Vector Classifier
[0.94s | 75.02MB] <Random Fourier Feature> 7500->2500 Random Fourier Feature created
  | <test data> Loading Images...
  |   | <IDC Dataset> started accounting
  |   |   | <Loader> Loading patient 10253...
  |   | [0.27s | 1.10MB] <Loader> loaded patient 10253
  |   |   | <Loader> Loading patient 10254...
  |   |   | <Loader> Loading patient 10261...

            [Details omitted]

  |   | [6.37s | 4.66MB] <Loader> loaded patient 13693
  |   |   | <Loader> Loading patient 13694...
  |   | <IDC Dataset> stopped accounting
  | [113.93s | 502.89MB] <IDC Dataset> 25143 images (10.0%) sampled from 254 patients
  | <training data> Loading Images...
  |   | <IDC Dataset> started accounting
  |   |   | <Loader> Loading patient 9257...
  |   |   | <Loader> Loading patient 9258...

            [Details omitted]

  |   | <IDC Dataset> stopped accounting
  | [84.02s | 516.57MB] <IDC Dataset> 25827 images (100.0%) sampled from 25 patients
  |   | <RF SVC> Computing RF SVC Classifier
  |   | [8.40s] <RF SVC> RFF SVC Computed
<Task> Classification experiment on new patients
  | <Tester> True Negative: 18126
  | <Tester> True Positive: 4116
  | <Tester> False Negative: 1588
  | <Tester> False Positive: 1997
  | <Tester> Total Tests: 25827
  | <Tester> Incorrect Tests: 3585.0
  | <Tester> Correct Tests: 22242.0
  | <Tester> Percent Error: 13.880822395167847
  | <Tester> Constant Classifier Baseline: 22.08541448871336
  | <Tester> Relative Improvement over Constant: 0.3714936886395512
[0.36s] <Tester> Done running tests.
  | <Tester> Time per test: 1.378298848930882e-05s
<Task> Classification verification on training data
  | <Tester> True Negative: 16185
  | <Tester> True Positive: 4704
  | <Tester> False Negative: 2715
  | <Tester> False Positive: 1539
  | <Tester> Total Tests: 25143
  | <Tester> Incorrect Tests: 4254.0
  | <Tester> Correct Tests: 20889.0
  | <Tester> Percent Error: 16.919222049874715
  | <Tester> Constant Classifier Baseline: 29.507218708984606
  | <Tester> Relative Improvement over Constant: 0.42660735948241
[0.35s] <Tester> Done running tests.
  | <Tester> Time per test: 1.3938018597950777e-05s
[213.03s] <RF> Program finished.
""".split('\n')

    s.loop()
