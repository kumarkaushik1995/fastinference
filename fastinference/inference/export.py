# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00b_inference.export.ipynb (unless otherwise specified).

__all__ = ['get_information']

# Cell
from fastai.vision.all import *

# Cell
def _gen_dict(tfm):
    "Grabs the `attrdict` and transform name from `tfm`"
    tfm_dict = attrdict(tfm, *tfm.store_attrs.split(','))
    if 'partial' in tfm.name:
        tfm_name = tfm.name[1].split(' --')[0]
    else:
        tfm_name = tfm.name.split(' --')[0]
    return tfm_dict, tfm_name

# Cell
def _make_tfm_dict(tfms, type_tfm=False):
    "Extracts transform params from `tfms`"
    tfm_dicts = {}
    for tfm in tfms:
        if hasattr(tfm, 'store_attrs') and not isinstance(tfm, AffineCoordTfm):
            if type_tfm or tfm.split_idx is not 0:
                tfm_dict,name = _gen_dict(tfm)
                tfm_dict = to_list(tfm_dict)
                tfm_dicts[name] = tfm_dict
    return tfm_dicts

# Cell
@typedispatch
def _extract_tfm_dicts(dl:TfmdDL):
    "Extracts all transform params from `dl`"
    type_tfm,use_images = True,False
    attrs = ['tfms','after_item','after_batch']
    tfm_dicts = {}
    for attr in attrs:
        tfm_dicts[attr] = _make_tfm_dict(getattr(dl, attr), type_tfm)
        if attr == 'tfms':
            if getattr(dl,attr)[0][1].name == 'PILBase.create':
                use_images=True
        if attr == 'after_item': tfm_dicts[attr]['ToTensor'] = {'is_image':use_images}
        type_tfm = False
    return tfm_dicts

# Cell
def get_information(dls): return _extract_tfm_dicts(dls[0])

# Cell
from fastai.tabular.all import *

# Cell
@typedispatch
def _extract_tfm_dicts(dl:TabDataLoader):
    "Extracts all transform params from `dl`"
    types = 'normalize,fill_missing,categorify'
    if hasattr(dl, 'categorize'): types += ',categorize'
    if hasattr(dl, 'regression_setup'): types += ',regression_setup'
    tfms = {}
    name2idx = {name:n for n,name in enumerate(dl.dataset) if name in dl.cat_names or name in dl.cont_names}
    idx2name = {v:k for k,v in name2idx.items()}
    cat_idxs = {name2idx[name]:name for name in dl.cat_names}
    cont_idxs = {name2idx[name]:name for name in dl.cont_names}
    names = {'cats':cat_idxs, 'conts':cont_idxs}
    tfms['encoder'] = names
    for t in types.split(','):
        tfm = getattr(dl, t)
        tfms[t] = to_list(attrdict(tfm, *tfm.store_attrs.split(',')))

    categorize = dl.procs.categorify.classes.copy()
    for i,c in enumerate(categorize):
        categorize[c] = {a:b for a,b in enumerate(categorize[c])}
        categorize[c] = {v: k for k, v in categorize[c].items()}
        categorize[c].pop('#na#')
        categorize[c][np.nan] = 0
    tfms['categorify']['classes'] = categorize
    new_dict = {}
    for k,v in tfms.items():
        if k == 'fill_missing':
            k = 'FillMissing'
            new_dict.update({k:v})
        else:
            new_dict.update({k.capitalize():v})
    return new_dict

# Cell
@patch
def to_fastinference(x:Learner, data_fname='data', model_fname='model', path=Path('.')):
    "Export data for `fastinference_onnx` or `_pytorch` to use"
    if not isinstance(path,Path): path = Path(path)
    dicts = get_information(x.dls)
    with open(path/f'{data_fname}.pkl', 'wb') as handle:
        pickle.dump(dicts, handle, protocol=pickle.HIGHEST_PROTOCOL)
    torch.save(x.model, path/f'{model_fname}.pkl')
