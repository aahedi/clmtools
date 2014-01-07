from buildlib import preprocess, buildshape, config
#from buildlib.buildpatch_mosse import build_patches
from buildlib.buildpatch import build_patches
from buildlib.buildscore import getScoring
import pickle
import numpy, json

buildPatches = True
buildScoring = True
cleanUp = True

# preprocess data
data_pca, data_patches, meanshape, cropsize = preprocess.preprocess(config.annotations, mirror = True)

#dp = {'data_pca' : data_pca, 'data_patches' : data_patches, 'meanshape' : meanshape, 'cropsize' : cropsize}
#fi = open("out.data", "w")
#pickle.dump(dp, fi)
#fi.close()

#fi = open("out.data", "r")
#data = pickle.load(fi)
#fi.close()
#data_pca = data['data_pca']
#data_patches = data['data_patches']
#meanshape = data['meanshape']
#cropsize = data['cropsize']

# build shape model
eigenVectors, eigenValues = buildshape.pca(data_pca.values(), num_components=20)
#eigenVectors, eigenValues = buildshape.spca(data_pca.values(), num_components=10, alpha=0.5)
mean = [numpy.mean(column) for column in meanshape.T]

if buildScoring:
	scoring = getScoring(data_pca, meanshape-mean)

for k,v in data_pca.iteritems():
		data_pca[k] = (v+meanshape)-mean
for k,v in data_patches.iteritems():
		data_patches[k] = (v+meanshape)-mean

# TODO: add values so that model is equally as wide/high as cropped images
# in our case: 170 x 178, i.e. add 85 to x-vals, and 89 to y-vals
meanshape = ((meanshape-mean)+[cropsize[0]/2,cropsize[1]/2])

if buildPatches:
	# build patch model
	#patchModel = build_patches(data_patches, 0.1, False)
	patchModel = build_patches(data_patches, 0.00000001, False)

# store
model = {}
if buildPatches:
	model['patchModel'] = patchModel
	model['patchModel']['canvasSize'] = [cropsize[0],cropsize[1]]
if buildScoring:
	model['scoring'] = scoring
model['shapeModel'] = {}
model['shapeModel']['eigenVectors'] = eigenVectors.T.tolist()
model['shapeModel']['eigenValues'] = eigenValues
model['shapeModel']['meanShape'] = meanshape.tolist()
model['shapeModel']['numEvalues'] = len(eigenValues)
model['shapeModel']['numPtsPerSample'] = meanshape.shape[0]

try:
  model['shapeModel']['nonRegularizedVectors'] = [0]
  model['hints'] = {}
  model['hints']['leftEye'] = meanshape[27,:].tolist()
  model['hints']['rightEye'] = meanshape[32,:].tolist()
  model['hints']['nose'] = meanshape[62,:].tolist()
except:
  import pdb;pdb.set_trace()

model['path'] = config.path

of = open("model.js","w")
of.write("var pModel = ")
of.write(json.dumps(model, indent=2))
of.write(";\n")
of.close()

if cleanUp:
  import shutil
  # delete /data/cropped folder
  shutil.rmtree(os.path.join(data_folder, "cropped/"))
  # delete /data/pcropped folder
  shutil.rmtree(os.path.join(data_folder, "pcropped/"))
  # delete /data/svmImages
  shutil.rmtree(os.path.join(data_folder, "svmImages/"))