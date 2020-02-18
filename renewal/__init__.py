import numpy as np
from scipy.stats import t, norm

class DataWrangler():
    @classmethod
    def Nxd_to_xrd(cls, N, x, d):
        # When you have N, the number of components
        r = np.zeros_like(x)
        r[0] = 5
        r = np.cumsum(r - (1 - d))
        r = np.hstack([[5], r[0:-1]])
        return x, r, d

    @classmethod
    def arrange(cls, x, r, d):
        idx = np.argsort(x)
        x = x[idx]
        r = r[idx]
        d = d[idx]
        return x, r, d

class NonParametric():
    def mcf(self, x, how='step'):
        x = np.atleast_1d(x)
        # Let's not assume we can predict above the highest measurement
        if how == 'step':
            idx = np.searchsorted(self.x, x, side='right') - 1
            mcf = self.mcf_hat[idx]
            mcf[np.where(x < self.x.min())] = 0
            mcf[np.where(x > self.x.max())] = np.nan
            mcf[np.where(x < 0)] = np.nan
            return mcf
        elif how == 'interp':
            mcf = np.hstack([[0], self.mcf_hat])
            x_data = np.hstack([[0], self.x])
            mcf = np.interp(x, x_data, mcf)
            mcf[np.where(x > self.x.max())] = np.nan
            return mcf

    def mcf_cb(self, x, bound='two-sided', how='step', 
               confidence=0.95, bound_type='exp', dist='z'):
        # Greenwoods variance using t-stat. Ref found:
        # http://reliawiki.org/index.php/Non-Parametric_Life_Data_Analysis
        assert bound_type in ['exp', 'normal']
        assert dist in ['t', 'z']
        x = np.atleast_1d(x)
        if bound in ['upper', 'lower']:
            if dist == 't':
                stat = t.ppf(1 - confidence, self.r - 1)
            else:
                stat = norm.ppf(1 - confidence, 0, 1)
            if bound == 'upper' : stat = -stat
        elif bound == 'two-sided':
            if dist == 't':
                stat = t.ppf((1 - confidence)/2, self.r - 1)
            else:
                stat = norm.ppf((1 - confidence)/2, 0, 1)
            stat = np.array([-1, 1]).reshape(2, 1) * stat

        if bound_type == 'exp':
            # Exponential Greenwood confidence
            mcf_cb = self.mcf_hat * np.exp(stat * np.sqrt(self.var)/self.mcf_hat)
        else:
            # Normal Greenwood confidence
            mcf_cb = self.mcf_hat + np.sqrt(self.var * self.mcf_hat**2) * stat
        # Let's not assume we can predict above the highest measurement
        if how == 'step':
            mcf_cb[np.where(x < self.x.min())] = 0
            mcf_cb[np.where(x > self.x.max())] = np.nan
            mcf_cb[np.where(x < 0)] = np.nan
            idx = np.searchsorted(self.x, x, side='right') - 1
            if bound == 'two-sided':
                mcf_cb = mcf_cb[:, idx].T
            else:
                mcf_cb = mcf_cb[idx]
        elif how == 'interp':
            if bound == 'two-sided':
                R1 = np.interp(x, self.x, mcf_cb[0, :])
                R2 = np.interp(x, self.x, mcf_cb[1, :])
                mcf_cb = np.vstack([R1, R2]).T
            else:
                mcf_cb = np.interp(x, self.x, mcf_cb)
            mcf_cb[np.where(x > self.x.max())] = np.nan
        return mcf_cb

    @classmethod
    def fit(cls, x, r, d):
        out = cls()

        x, r, d = DataWrangler.arrange(x, r, d)
        
        out.x = x
        out.r = r
        out.d = d

        out.mcf_hat = np.cumsum(d/r)
        var = 1./r**2 * (d*(1 - 1./r)**2 + (r - d)*(0 - 1./r)**2)
        var = (d > 0).astype(np.int) * var
        out.var = np.cumsum(var)

        return out


class Parametric():

    def __init__(self, dist):
        self.dist = dist

    @classmethod
    def fit(cls, x, r, d, model='Duane'):
        assert model in ['Duane', 'Crow', 'Log-Linear', 'Best']
        dist = DISTS[model]
        out = cls(dist)

        x, r, d = DataWrangler.arrange(x, r, d)
        
        out.x = x
        out.r = r
        out.d = d

        out.mcf_hat = np.cumsum(d/r)


        fun lambda t : dist.MCF()

        out.mcf = lambda x : 

        return out

class Duane():
    # Parameterisation done in accordance with:
    # http://reliawiki.org/index.php/Duane_Model
    def __init__(self):
        self.k = 2

    def MCF(self, x, b, alpha):
        return b * T**alpha

    def rocof(self, x, b, alpha):
        return (1./b) * x**(-alpha)




DISTS = {
    'Duane' : Duane
}




