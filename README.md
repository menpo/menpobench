## What is menpobench?

menpobench is a Python package that implements a standardized way to test
deformable models, like the ones available in
[menpofit](https://github.com/menpo/menpofit). These algorithms find key
*feature points* or *landmarks* in images of objects. For instance, such a
deformable model could be trained to accurately find facial features like the
*nose tip* or *left mouth corner* on images of people's faces. They are
sometimes called *landmark localization* techniques.

Examples of such algorithms are:

- Active Appearance Model (AAM)
- Constrained Local Model (CLM)
- Supervised Decent Method (SDM)
- Explicit Shape Regression (ESR)

Such methods need to **initialized** in the vicinity of the object in the image
for them to properly converge - you can't expect to run an AAM on a whole image
for instance. Instead, an **object detector** (like the ones provided in
[menpodetect](https://github.com/menpo/menpodetect)) is first employed in order
to find **bounding boxes** around candidate objects in the scene. The method
starts from this position, and attempts to localize points.

## How are different methods compared by reserchers?

It's important that we can fairly compare algorithms against each other in order
to evaluate different technique's strengths and weaknesses. This is generally
done by training each deformable model on a large database of training images
with ground truth data. This database is known as the *training set*. This
means for each image, both the *bounding box* (the initialization) and the
*ground truth shape* (the actual landmarks) is made available to the algorithm
in order to learn how to localize landmarks.

At *test time*, where we are interested in evaluating the performance of the
method, a *test set* of images is provided to the algorithm. This time, only
bounding boxes are provided for each image, and the method must attempt to find
the landmarks automatically. For every image in the test set, the ground truth
result is known. The method's performance is quantified by an *error metric*  -
the lower this number, the better the performance of the method. A perfect
method would score 0.0 error on every image in the test set.

### What is the error metric exactly? How is it computed?

A simple choice for the error metric would be to simply average the distance
between the ground truth and the prediction for each landmark point on an image.
More formally, this is referred to as the *mean point-to-point euclidean error
metric*.

This basic approach suffers from a problem though. The 'units' for this basic
error is number of pixels. However, different images are of different
resolutions - in the test-set there will be some images that are high resolution
and the object itself dominates the whole frame. In such images, a relatively
large mean point-to-point error may actually be represent a very good
localization performance.

Conversely, some images are of low resolution, and the object maybe be small in
the frame. In such examples, a small absolute mean point-to-point error would be
a disappointing fitting performance - the predicted landmarks may not even lie
on the object for instance.

The solution to this problem is simply to *normalize* the error in some way by
the *size of the object*. There are a number of ways to do this. In facial
analysis, currently the most common domain of applications for deformable
models, popularly choices include normalizing by the *interocular distance* -
the distance between the persons two eyes. Another popular option is to
normalize by the *face size*, defined as the area of the bounding box divided by
two.

It's important to point out that the manner of normalization is not so critical,
so long as it is applied consistently when evaluating related methods.

## Why make menpobench open source?

Every researcher currently has their own test harness for evaluating techniques,
which makes it very challenging to compare across different papers fairly.
Although authors provide some details of the testing mechanism in the papers's
text, it is often insufficient to fully reproduce the results presented in the
paper. Common issues include:

1. **Incosistent normalization methods**. Different authors follow different
schemes for normalization of the error metric. Between two papers, the same
exact training and test data may be used, but one may normalize by face shape
and the other by interocular distance, making the results incomparable.

2. **Tweaks to the training/testing data** Authors will very commonly test on
the same datasets, which should make results portable between papers. Popular
examples of open databases in facial analysis include Annotated Faces in the
Wild (AFW) Labeled Face Parts in the Wild (LFPW), and iBUG. However, authors
will sometimes weed out problematic images, or use different object detectors or
schemes for bounding boxes (e.g. very tight around the object, or somewhat
looser with a boarder around the object). Not knowing the exact data used for
training and testing can lead to different opinions of performance.

3. **Minor bugs** Evaluation code is seldom open source, so it cannot be
scrutinized by the wider community to check for innocent errors.

menpobench provides the community with an open source benchmarking suite
for deformable models. menpobench provides all the boilerplate code needed to
initialize, test, and evaluate a deformable model. By using menpobench:

1. **Your results are comparable with others**. You can instantly compare your
new method against many others for a variety of datasets, giving you a clearer
picture of how well you are performing.

2. **Other researchers can reproduce your evaluation** Other reserachers can
take your technique (even as a closed source binary) and evalulate it however
they please within the menpobench framework.

3. **You don't have to worry about making mistakes in your evaluation code**
menpobench will have many eyes on it checking for errors, making it far less
likely to have bugs.


## Is menpobench just about methods implemented in Menpo?

**No**. You can use menpobench to test your own methods written in any language
you want.

## Do I need to learn Python to use menpobench?

**No**. menpobench is a command line tool configured by simple YAML files.
Results are returned in standard containers like PDFs and CSV files. You could
take the results from menpobench, and easily import then into Matlab for
analysis.

## How do I run tests in menpobench?

The main interface for using menpobench is a command line utility,
imaginatively called `menpobench`. Once you have installed menpobench, you
will have this tool available globally. For instance, to learn more about the
parameters that `menpobench` takes, try running:
```sh
> menpobench -h
```
In a terminal[1].

Benchmark runs are described in a simple
[YAML](https://en.wikipedia.org/wiki/YAML) file. An example looks like:

```yaml
training_data:
    - lfpw_38_dlib_train
    - ibug_38_dlib_train
testing_data:
    - lfpw_38_dlib_test
methods:
    - sdm
    - aam
untrainable_methods:
    - intraface
```

You would save a text file like this with the name of your experiment, e.g.
`sdm_vs_aam.yaml`. To run the benchmark, simply provide this text file to
the `menpobench` command:

```sh
> menpobench ./path/to/sdm_vs_aam.yaml
```

In this instance, our YAML describes an experiment where we want to compare the
performance of an Supervised Decent Method (SDM) model against an Active
Appearance Model (AAM) and the popular closed-source
[intraface](http://www.humansensing.cs.cmu.edu/intraface/) SDM implementation.
The test set is chosen from a standard list of test-sets that menpobench
provides. menpobench will:

1. Train an AAM and SDM on LFPW and iBUG using the 38 point markup and
[dlib](http://dlib.net) object detector bounding boxes for initialization.

2. Evaluate both the AAM and SDM trained by testing on the LFPW test set, also
using 38 points and dlib object detection bounding boxes.

3. Additionally evaluate against intraface.

4. Report back the results of the evaluation in a normalization-agnostic way, so
you can interpret it in a number of ways.

## Wait but you are comparing against intraface, which isn't part of menpofit

menpobench tries hard to automatically acquire testing data and provide easy
ways to call other popular methods. Where possible we will handle the
acquisition of these other tools and provide a hook into them from our standard
testing suite.

In other words, by using menpobench, you can immediately compare against these
other popular techniques. You don't need to download them and set them up
yourself[2].

## Isn't menpobench going to take forever to run?

No. [Team Menpo](https://twitter.com/teammenpo) runs many popular benchmark
options every night on a continuous integration server and records the results.
These cached results are provided in the copy menpobench you download. By
default menpobench will retrieve test results from this cached database rather
than re-runing the test, which means evaluations can often complete
instantaneously.

## I don't trust Team Menpo, I'll run my own tests thank you very much.

That's no problem, just pass the `--force` option to `menpobench` and reproduce
the results on your own machine.

## How do I know what keys are available?

You can run `menpobench --list` to output an exhaustive list of what predefined
datasets, methods, and untrainable methods are provided in menpobench.

## How do I know what a key actually does?

Keys that you can use in the schema simply map to python files in the
[predefined folder inside menpobench](https://github.com/menpo/menpobench/tree/master/menpobench/predefined).
You can inspect these files to see exactly how a given part of menpobench is
implemented. If you think we are doing something incorrectly or suboptimally,
issue a PR and tell us about it.

## I want to test on a dataset or on a method that is not shipped as part of menpobench - how do I do that?

In leiu of providing names like `lfpw_38_dlib_train` which will refer to a
builtin component of menpobench, you can provide the path to your own python
file. This python file will have to follow the same design patterns as the
builtin files used in the relevant section. For instance, all dataset loading
components are actually python files with a callable inside them called
`generate_dataset()`. This is expected to be a generator yielding Menpo Image
objects with landmarks attached with specific group names:

- `bbox` - the bounding box annotation for this image
- `gt_shape` - the ground truth shape of this image

A simple example of a database loading component looks like this[3]:

```py
import menpo.io as mio
from pathlib import Path
DB_PATH = Path('/vol/atlas/database/my_dataset')
# lets assume this database has the form
#
# ./my_dataset
#    ./training_images
#      ./IMG_000.jpg
#      ...
#    ./gt
#      ./IMG_000.ljson
#      ...
#    ./bbox
#      ./IMG_000.ljson
#      ...
#
def generate_dataset():
    for path in (DB_PATH / 'training_images').glob('*.jpg'):
        im = mio.import_image(path)
        im.landmarks['gt'] = mio.import_landmark_file(DB_PATH / 'gt' / (path.stem + '.ljson'))
        im.landmarks['bbox'] = mio.import_landmark_file(DB_PATH / 'bbox' / (path.stem + '.ljson'))
        yield im
```

If you saved this file as `./path/to/my_dataset.py`, you could use it for
training in our previous example as

```yaml
training_data:
    - lfpw_38_dlib_train
    - ibug_38_dlib_train
    - ./path/to/my_dataset.py
testing_data:
    - lfpw_38_dlib_test
methods:
    - sdm
    - aam
untrainable_methods:
    - intraface
```


[1]: If you have installed menpobench inside a conda env as recommended, you
will first have to activate the environment before the tool is available, e.g.
`source activate mymenpoenv`.

[2]: Of course, if the tool in question needs Matlab you'll need to have that
on your system yourself.

[3]: You'll notice that predefined datasets have a quirky little context
manager inside them in order to lazily load a menpobench-managed dataset
(and to not have absolute paths), but they are in essence the same as the
 example shown here.
