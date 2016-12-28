# encoding: shift_jis
import numpy
import random
import math
import pylab
import matplotlib

# �m�����v�Z���邽�߂̃N���X
class GaussWishart():
    def __init__(self,dim, mean, var):
        # ���O���z�̃p�����[�^
        self.__dim = dim
        self.__r0 = 1
        self.__nu0 = dim + 2
        self.__m0 = mean.reshape((dim,1))
        self.__S0 = numpy.eye(dim, dim ) * var

        self.__X = numpy.zeros( (dim,1) )
        self.__C = numpy.zeros( (dim, dim) )
        self.__r = self.__r0
        self.__nu = self.__nu0
        self.__N = 0

        self.__update_param()

    def __update_param(self):
        self.__m = (self.__X + self.__r0 * self.__m0)/(self.__r0 + self.__N )
        self.__S = - self.__r * self.__m * self.__m.T + self.__C + self.__S0 + self.__r0 * self.__m0 * self.__m0.T;


    def add_data(self, x ):
        x = x.reshape((self.__dim,1))  # �c�x�N�g���ɂ���
        self.__X += x
        self.__C += x.dot( x.T )
        self.__r += 1
        self.__nu += 1
        self.__N += 1

        self.__update_param()

    def delete_data(self, x ):
        x = x.reshape((self.__dim,1))  # �c�x�N�g���ɂ���
        self.__X -= x
        self.__C -= x.dot( x.T )
        self.__r -= 1
        self.__nu -= 1
        self.__N -= 1

        self.__update_param()

    def calc_loglik(self, x):
        def _calc_loglik(self):
            p = - self.__N * self.__dim * 0.5 * math.log( math.pi )
            p+= - self.__dim * 0.5 * math.log( self.__r)
            p+= - self.__nu * 0.5 * math.log( numpy.linalg.det( self.__S ) );

            for d in range(1,self.__dim+1):
                p += math.lgamma( 0.5*(self.__nu+1-d) )

            return p

        # log(P(X))
        p1 = _calc_loglik( self )

        # log(P(x,X))
        self.add_data(x)
        p2 = _calc_loglik( self )
        self.delete_data(x)

        # log(P(x|X) = log(P(x,X)) - log(P(X))
        return p2 - p1

    def get_mean(self):
        return self.__m

    def get_num_data(self):
        return self.__N

# �K�E�X���z�̓�������`��
def draw_gauss( dist, rangex, rangey ):
    shape = ( len(rangex), len(rangey) )
    xx = numpy.zeros(shape)
    yy = numpy.zeros(shape)
    probs = numpy.zeros(shape)
    for i,x in enumerate(rangex):
        for j,y in enumerate(rangey):
            xx[j,i] = x
            yy[j,i] = y
            probs[j,i] = calc_probability( dist, numpy.array([x, y]) )
    pylab.contour( xx, yy, probs )

    # ���ϒl��`��
    m = dist.get_mean()
    pylab.plot( m[0], m[1], "x" )


# �O���t�ɕ`��
def draw_data( data, classes, distributions, colors = ("r" , "b" , "g" , "c" , "m" , "y" , "k" )):
    pylab.clf()
    # �f�[�^��`��
    for d,k in zip(data, classes):
        pylab.scatter( d[0] , d[1] , color=colors[k] )

    # ���z��`��
    rangex = numpy.linspace( numpy.min(data[:,0]), numpy.max(data[:,0]), 50 )
    rangey = numpy.linspace( numpy.min(data[:,1]), numpy.max(data[:,1]), 50 )
    for dist in distributions:
        draw_gauss( dist, rangex, rangey )


def draw_line( p1 , p2 , color="k" ):
    pylab.plot( [p1[0], p2[0]] , [p1[1],p2[1]], color=color )

def plot0(data, classes, distributions):
    draw_data( data, classes, distributions )
    pylab.draw()
    pylab.pause(1.0)

def plot1(d, data, classes, distributions):
    draw_data( data, classes, distributions )
    for k in range(len(distributions)):
        draw_line( d , distributions[k].get_mean() )
    pylab.draw()
    pylab.pause(0.1)

def plot2(d, k_new, data, classes, distributions):
    draw_data( data, classes, distributions )
    draw_line( d , distributions[k_new].get_mean() , "y" )
    pylab.draw()
    pylab.pause(0.1)

def plot3(data, classes, distributions):
    pylab.ioff()
    draw_data( data, classes, distributions )
    for d,k in zip(data,classes):
        draw_line( d , distributions[k].get_mean() )
    pylab.show()

def calc_probability( dist, d ):
    return dist.get_num_data() * math.exp( dist.calc_loglik( d ) )

def sample_class( d, distributions ):
    K = len(distributions)
    P = [ 0.0 ] * K

    # �ݐϊm�����v�Z
    P[0] = calc_probability( distributions[0], d )
    for k in range(1,K):
        P[k] = P[k-1] + calc_probability( distributions[k], d )

    # �T���v�����O
    rnd = P[K-1] * random.random()
    for k in range(K):
        if P[k] >= rnd:
            return k

# gmm���C��
def gmm( data , K ):
    pylab.ion()

    # �f�[�^�̎���
    dim = len(data[0])

    # �f�[�^�������_���ɕ���
    classes = numpy.random.randint( K , size=len(data) )

    # �K�E�X-�E�B�V���[�ƕ��z�̃p�����[�^���v�Z
    mean = numpy.mean( data, axis=0 )
    distributions = [ GaussWishart(dim, mean , 0.1) for _ in range(K) ]
    for i in range(len(data)):
        c = classes[i]
        x = data[i]
        distributions[c].add_data(x)

    # �O���t�\��
    plot0(data, classes, distributions)

    for it in range(100):
        # ���C���̏���
        for i in range(len(data)):
            d = data[i]
            k_old = classes[i]  # ���݂̃N���X

            # �f�[�^���N���X���珜���p�����[�^���X�V
            distributions[k_old].delete_data( d )
            classes[i] = -1

            # �O���t�\��
            plot1(d, data, classes, distributions)

            # �V���ȃN���X���T���v�����O
            k_new = sample_class( d , distributions )

            # �T���v�����O���ꂽ�N���X�̃p�����[�^���X�V
            classes[i] = k_new
            distributions[k_new].add_data( d )

            # �O���t�\��
            plot2(d, k_new, data, classes, distributions)


    # �ŏI�I�Ȍ��ʂ�\��
    plot3(data, classes, distributions)


def main():
    data = numpy.loadtxt( "data2.txt" )
    gmm( data , 2 )


if __name__ == '__main__':
    main()